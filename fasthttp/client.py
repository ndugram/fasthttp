import logging
import time
from typing import Annotated

import httpx
from annotated_doc import Doc
from pydantic import ValidationError

from fasthttp.middleware import MiddlewareManager
from fasthttp.security import (
    CircuitOpenError,
    Security,
    SecurityError,
    SSRFBlockedError,
)

from .exceptions import (
    FastHTTPBadStatusError,
    FastHTTPConnectionError,
    FastHTTPRequestError,
    FastHTTPTimeoutError,
    log_success,
)
from .response import Response
from .routing import Route


class HTTPClient:
    """
    HTTP client responsible for sending HTTP requests.

    This class manages low-level request execution using httpx,
    applies per-method request configuration (headers, timeout, redirects),
    logs request lifecycle events, and returns normalized Response objects.
    """

    def __init__(
        self,
        request_configs: Annotated[
            dict,
            Doc(
                """
                Dictionary mapping HTTP methods to default request configurations.
                Each key is an HTTP method (GET, POST, PUT, DELETE, etc.) and
                the value is a dict containing default headers, timeout, and
                other request options for that method.
                """
            )
        ],
        logger: Annotated[
            logging.Logger,
            Doc(
                """
                Logger instance for recording request lifecycle events including
                errors, success responses, and middleware processing. Should be
                configured by the application for appropriate log output.
                """
            )
        ],
        middleware_manager: Annotated[
            MiddlewareManager | None,
            Doc(
                """
                Optional MiddlewareManager instance for processing middleware
                hooks (before_request, after_response, on_error). If None,
                no middleware processing will be applied. Defaults to None.
                """
            )
        ] = None,
        security: Annotated[
            Security | None,
            Doc(
                """
                Optional Security instance for built-in security features.
                If None, security is enabled by default with all protections.
                """
            )
        ] = None,
    ) -> None:
        self.request_configs = request_configs
        self.logger = logger
        self.middleware_manager = middleware_manager
        self.security = security

    def _validate_request(self, route: Route) -> bool:
        if not route.request_model:
            return True

        try:
            if route.json:
                route.request_model.model_validate(route.json)
            elif route.data and isinstance(route.data, dict):
                route.request_model.model_validate(route.data)
            return True
        except ValidationError as e:
            self.logger.error("Request validation failed: %s", e)
            return False

    async def _prepare_config(self, route: Route, config: dict) -> dict:
        headers = dict(config.get("headers") or {})
        headers.setdefault("User-Agent", "fasthttp/1.0.2")
        config["headers"] = headers

        if self.middleware_manager:
            config = await self.middleware_manager.process_before_request(route, config)

        for dep in route.dependencies:
            config = await dep(route, config)

        return config

    async def _apply_security_checks(self, route: Route) -> bool:
        if not self.security:
            return True

        try:
            await self.security.pre_request(route.url, route.method)
            return True
        except SSRFBlockedError as e:
            self.logger.error("SSRF blocked: %s", e)
            return False
        except CircuitOpenError as e:
            self.logger.error("Circuit breaker open: %s", e)
            return False
        except SecurityError as e:
            self.logger.error("Security error: %s", e)
            return False

    def _get_timeout_config(self, config: dict) -> httpx.Timeout:
        if self.security:
            if self.security.connect_timeout:
                return httpx.Timeout(self.security.connect_timeout)
            return httpx.Timeout(self.security.timeout)

        timeout = config.get("timeout", 30.0)
        if timeout is not None:
            return httpx.Timeout(timeout)
        return httpx.Timeout(30.0)

    def _log_request(self, route: Route, config: dict) -> None:
        if self.security:
            masked_headers = self.security.mask_headers_for_logging(config["headers"])
            self.logger.debug(
                "→ %s %s | headers=%s",
                route.method,
                route.url,
                masked_headers,
            )
        else:
            self.logger.debug(
                "→ %s %s | headers=%s",
                route.method,
                route.url,
                config.get("headers"),
            )

    async def _check_response_security(
        self,
        route: Route,
        response: httpx.Response
    ) -> None:
        if not self.security:
            return

        self.security.release_slot()
        self.security.check_response_headers(dict(response.headers))
        self.security.check_response(
            content=response.content,
            content_type=response.headers.get("content-type"),
            status_code=response.status_code,
        )
        await self.security.post_request(route.url, route.method, True)

    async def _handle_bad_status(
        self,
        route: Route,
        config: dict,
        response: httpx.Response
    ) -> None:
        error = FastHTTPBadStatusError(
            message=f"HTTP {response.status_code}",
            url=route.url,
            method=route.method,
            status_code=response.status_code,
            response_body=response.text,
        )
        error.log()

        if self.middleware_manager:
            await self.middleware_manager.process_on_error(error, route, config)

    async def _handle_error(
        self,
        route: Route,
        config: dict,
        error: Exception,
        error_class: type[FastHTTPRequestError],
        **kwargs
    ) -> None:
        if self.security:
            self.security.release_slot()
            await self.security.post_request(route.url, route.method, False, error)

        exc = error_class(
            message=str(error) or "Request failed",
            url=route.url,
            method=route.method,
            **kwargs
        )
        exc.log()

        if self.middleware_manager:
            await self.middleware_manager.process_on_error(exc, route, config)

    def _build_response(
        self,
        route: Route,
        config: dict,
        response: httpx.Response
    ) -> Response:
        return Response(
            status=response.status_code,
            text=response.text,
            headers=dict(response.headers),
            method=route.method,
            req_headers=config.get("headers"),
            query=route.params,
            req_json=route.json,
            req_data=route.data,
        )

    async def _process_handler_result(
        self,
        response: Response,
        handler_result: object
    ) -> Response:
        if isinstance(handler_result, Response):
            return handler_result
        if isinstance(handler_result, str):
            response.text = handler_result
        response._handler_result = handler_result
        return response

    async def _execute_request(
        self,
        client: httpx.AsyncClient,
        route: Route,
        config: dict,
        timeout_config: httpx.Timeout
    ) -> tuple[httpx.Response, float] | None:
        start = time.perf_counter()

        try:
            resp = await client.request(
                method=route.method,
                url=route.url,
                headers=config.get("headers"),
                params=route.params,
                json=route.json,
                content=route.data,
                timeout=timeout_config,
                follow_redirects=False,
            )
            elapsed = (time.perf_counter() - start) * 1000
            return resp, elapsed
        except httpx.ConnectError as e:
            await self._handle_error(route, config, e, FastHTTPConnectionError)
        except httpx.TimeoutException as e:
            await self._handle_error(
                route, config, e, FastHTTPTimeoutError,
                timeout=config.get("timeout", "default")
            )
        except SecurityError as e:
            if self.security:
                self.security.release_slot()
                await self.security.post_request(route.url, route.method, False, e)
            self.logger.error("Security error: %s", e)
        except Exception as e:
            await self._handle_error(route, config, e, FastHTTPRequestError)

        return None

    async def send(
        self,
        client: httpx.AsyncClient,
        route: Route
    ) -> Response | None:
        if not self._validate_request(route):
            return None

        config = self.request_configs.get(route.method, {})
        config = await self._prepare_config(route, config)

        if not await self._apply_security_checks(route):
            return None

        if self.security:
            await self.security.acquire_slot()
            config["headers"] = self.security.sanitize_request_headers(config["headers"])

        timeout_config = self._get_timeout_config(config)
        self._log_request(route, config)

        result = await self._execute_request(client, route, config, timeout_config)
        if not result:
            return None

        resp, elapsed = result
        await self._check_response_security(route, resp)

        if resp.status_code >= 400:
            await self._handle_bad_status(route, config, resp)
            return None

        log_success(route.url, route.method, resp.status_code, elapsed)

        response = self._build_response(route, config, resp)

        if self.middleware_manager:
            response = await self.middleware_manager.process_after_response(
                response, route, config
            )

        handler_result = await route.handler(response)
        return await self._process_handler_result(response, handler_result)

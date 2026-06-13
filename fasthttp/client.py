import logging
import time
from typing import Annotated, Any

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

from .__meta__ import __version__
from .auth import resolve_auth
from .exceptions import (
    FastHTTPBadStatusError,
    FastHTTPConnectionError,
    FastHTTPError,
    FastHTTPRequestError,
    FastHTTPTimeoutError,
    log_success,
)
from .middleware.retry import RetrySignal
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
            ),
        ],
        logger: Annotated[
            logging.Logger,
            Doc(
                """
                Logger instance for recording request lifecycle events including
                errors, success responses, and middleware processing. Should be
                configured by the application for appropriate log output.
                """
            ),
        ],
        middleware_manager: Annotated[
            MiddlewareManager | None,
            Doc(
                """
                Optional MiddlewareManager instance for processing middleware
                hooks (before_request, after_response, on_error). If None,
                no middleware processing will be applied. Defaults to None.
                """
            ),
        ] = None,
        security: Annotated[
            Security | None,
            Doc(
                """
                Optional Security instance for built-in security features.
                If None, security is enabled by default with all protections.
                """
            ),
        ] = None,
        startup_uuid: Annotated[
            str | None,
            Doc(
                """
                UUID generated on application startup.
                Will be sent as X-Request-ID header in all requests.
                """
            ),
        ] = None,
        *,
        raise_for_status: Annotated[
            bool,
            Doc(
                """
                Whether to raise FastHTTPBadStatusError on 4xx/5xx responses.

                When True, any response with a status code >= 400 will raise
                FastHTTPBadStatusError instead of returning None.

                Defaults to False.
                """
            ),
        ] = False,
    ) -> None:
        self.request_configs = request_configs
        self.logger = logger
        self.middleware_manager = middleware_manager
        self.security = security
        self.startup_uuid = startup_uuid
        self.raise_for_status = raise_for_status

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
        config = dict(config)
        headers = dict(config.get("headers") or {})
        headers.setdefault("User-Agent", f"fasthttp/{__version__}")

        if self.startup_uuid:
            headers.setdefault("X-Request-ID", self.startup_uuid)

        config["headers"] = headers

        if self.middleware_manager:
            config = await self.middleware_manager.process_before_request(route, config)  # type: ignore

        dep_cache: dict[int, dict] = {}
        for dep in route.dependencies:
            func_id = id(dep.func)
            if dep.use_cache and func_id in dep_cache:
                config = dep_cache[func_id]
            else:
                config = await dep(route, config)
                if dep.use_cache:
                    dep_cache[func_id] = config

        if self.security:
            body: dict | list | str | bytes | None = route.json or route.data  # type: ignore
            config["headers"] = self.security.sign_request(
                route.method,
                route.url,
                body,
                dict(config.get("headers") or {}),
            )

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
        user_timeout = config.get("timeout")
        if user_timeout is not None:
            return httpx.Timeout(user_timeout)
        if self.security:
            if self.security.connect_timeout:
                return httpx.Timeout(self.security.connect_timeout)
            return httpx.Timeout(self.security.timeout)
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
        self, route: Route, response: httpx.Response
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
        await self.security.post_request(route.url, route.method, success=True)

    async def _handle_bad_status(
        self, route: Route, config: dict, response: httpx.Response
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
            await self.middleware_manager.process_on_error(error, route, config)  # type: ignore

        if self.raise_for_status or route.raise_for_status:
            raise error

    async def _handle_error(
        self,
        route: Route,
        config: dict,
        error: Exception,
        error_class: type[FastHTTPError],
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        if self.security:
            self.security.release_slot()
            await self.security.post_request(
                route.url, route.method, success=False, error=error
            )

        exc = error_class(
            message=str(error) or "Request failed",
            url=route.url,
            method=route.method,
            **kwargs,
        )
        exc.log()

        if self.middleware_manager:
            await self.middleware_manager.process_on_error(exc, route, config)  # type: ignore

    def _build_response(
        self, route: Route, config: dict, response: httpx.Response
    ) -> Response:
        resp = Response(
            status=response.status_code,
            text=response.text,
            headers=dict(response.headers),
            method=route.method,
            req_headers=config.get("headers"),
            query=route.params,
            req_json=route.json,
            req_data=route.data,
            content=response.content,
        )
        resp._url = route.url  # noqa: SLF001
        return resp

    async def _process_handler_result(
        self, response: Response, handler_result: object
    ) -> Response:
        if isinstance(handler_result, Response):
            return handler_result
        if isinstance(handler_result, str):
            response.text = handler_result
        response._handler_result = handler_result  # noqa: SLF001
        return response

    async def _execute_request(
        self,
        client: httpx.AsyncClient,
        route: Route,
        config: dict,
        timeout_config: httpx.Timeout,
        *,
        raise_errors: bool = False,
    ) -> tuple[httpx.Response, float] | None:
        if route.skip_request:
            return None

        start = time.perf_counter()

        try:
            resp = await client.request(
                method=route.method,
                url=route.url,
                headers=config.get("headers"),
                params=config.get("params", route.params),
                json=route.json,
                content=route.data,  # type: ignore
                timeout=timeout_config,
                follow_redirects=False,
                auth=resolve_auth(route.auth),
            )
            elapsed = (time.perf_counter() - start) * 1000
            return resp, elapsed
        except httpx.ConnectError as e:
            if raise_errors:
                raise
            await self._handle_error(route, config, e, FastHTTPConnectionError)
        except httpx.TimeoutException as e:
            if raise_errors:
                raise
            await self._handle_error(
                route,
                config,
                e,
                FastHTTPTimeoutError,
                timeout=config.get("timeout", "default"),
            )
        except SecurityError as e:
            if raise_errors:
                raise
            if self.security:
                self.security.release_slot()
                await self.security.post_request(
                    route.url, route.method, success=False, error=e
                )
            self.logger.error("Security error: %s", e)
        except Exception as e:
            if raise_errors:
                raise
            await self._handle_error(route, config, e, FastHTTPRequestError)

        return None

    async def send(self, client: httpx.AsyncClient, route: Route) -> Response | None:  # noqa: C901
        if not self._validate_request(route):
            return None

        config = self.request_configs.get(route.method, {})
        config = await self._prepare_config(route, config)

        if "_fasthttp_cached_response" in config:
            cached = config["_fasthttp_cached_response"]
            handler_result = await route.handler(cached)
            return await self._process_handler_result(cached, handler_result)

        if not await self._apply_security_checks(route):
            return None

        if self.security:
            await self.security.acquire_slot()
            config["headers"] = self.security.sanitize_request_headers(
                config["headers"]
            )

        timeout_config = self._get_timeout_config(config)
        self._log_request(route, config)

        retry_middleware = self._get_retry_middleware()
        max_attempts = (retry_middleware.max_retries + 1) if retry_middleware else 1
        last_error: Exception | None = None

        for attempt in range(max_attempts):
            try:
                result = await self._execute_request(
                    client, route, config, timeout_config, raise_errors=True
                )

                if route.skip_request:
                    empty_response = Response(
                        status=200,
                        text="",
                        headers={},
                        method=route.method,
                    )
                    empty_response._url = route.url  # noqa: SLF001
                    empty_response._response_model = route.response_model  # noqa: SLF001
                    handler_result = await route.handler(empty_response)
                    return await self._process_handler_result(
                        empty_response, handler_result
                    )

                if not result:
                    return None

                resp, elapsed = result

                try:
                    await self._check_response_security(route, resp)
                except SecurityError as e:
                    self.logger.error("Response security check failed: %s", e)
                    if self.security:
                        self.security.release_slot()
                    return None

                if resp.status_code >= 400:
                    if self.middleware_manager:
                        built = self._build_response(route, config, resp)
                        try:
                            await self.middleware_manager.process_after_response(
                                built, route, config  # type: ignore
                            )
                        except RetrySignal:
                            if attempt < max_attempts - 1:
                                continue
                            return None

                    error_model = route.responses.get(resp.status_code)
                    if error_model:
                        if isinstance(error_model, dict):
                            error_model = error_model.get("model")
                        if error_model:
                            response = self._build_response(route, config, resp)
                            try:
                                error_data = response.json()
                                validated = error_model.model_validate(error_data)
                                response._handler_result = validated  # noqa: SLF001
                                handler_result = await route.handler(response)
                                return await self._process_handler_result(
                                    response, handler_result
                                )
                            except Exception:  # noqa: S110, BLE001
                                pass
                    await self._handle_bad_status(route, config, resp)
                    return None

                log_success(route.url, route.method, resp.status_code, elapsed)

                response = self._build_response(route, config, resp)
                response._response_model = route.response_model  # noqa: SLF001

                if self.middleware_manager:
                    response = await self.middleware_manager.process_after_response(
                        response,
                        route,
                        config,  # type: ignore
                    )

                handler_result = await route.handler(response)
                return await self._process_handler_result(response, handler_result)

            except RetrySignal:
                if attempt < max_attempts - 1:
                    continue
                return None
            except Exception as e:  # noqa: BLE001
                last_error = e
                if self.middleware_manager:
                    try:
                        await self.middleware_manager.process_on_error(
                            e, route, config  # type: ignore
                        )
                    except RetrySignal:
                        if attempt < max_attempts - 1:
                            continue
                        return None
                break

        if last_error is not None:
            self.logger.error("Request failed after retries: %s", last_error)

        return None

    def _get_retry_middleware(self) -> Any:  # noqa: ANN401
        """Find RetryMiddleware in the middleware chain if present."""
        from fasthttp.middleware.retry import RetryMiddleware

        if not self.middleware_manager:
            return None
        for mw in self.middleware_manager.middlewares:
            if isinstance(mw, RetryMiddleware):
                return mw
        return None

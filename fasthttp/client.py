import asyncio
import logging
import time
from typing import Annotated

import httpx
from annotated_doc import Doc

from fasthttp.middleware import MiddlewareManager

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
    ) -> None:
        self.request_configs = request_configs
        self.logger = logger
        self.middleware_manager = middleware_manager

    async def send(
        self,
        client: httpx.AsyncClient,
        route: Route
    ) -> Response | None:
        """
        Send a single HTTP request based on a Route definition.

        This method:
        - Applies request configuration based on HTTP method
        - Executes before_request middleware hooks
        - Sends the request using an existing httpx AsyncClient
        - Measures request execution time
        - Logs request lifecycle events
        - Executes after_response middleware hooks
        - Executes on_error middleware hooks on errors
        - Automatically handles and logs errors
        - Executes the route handler with the Response object

        Returns:
        - Response instance if the request was successful
        - Modified Response if the handler returned a string or Response
        - None if a connection or timeout error occurred
        """
        config = self.request_configs.get(route.method, {})

        headers = dict(config.get("headers") or {})
        headers.setdefault("User-Agent", "fasthttp/0.1.11")
        config["headers"] = headers
        if self.middleware_manager:
            config = await self.middleware_manager.process_before_request(route, config)

        self.logger.debug(
            "→ %s %s | headers=%s",
            route.method,
            route.url,
            config.get("headers"),
        )

        start = time.perf_counter()

        timeout_config = (
            httpx.Timeout(config.get("timeout", 30.0))
            if config.get("timeout") is not None
            else httpx.Timeout(30.0)
        )

        try:
            resp = await client.request(
                method=route.method,
                url=route.url,
                headers=config.get("headers"),
                params=route.params,
                json=route.json,
                content=route.data,
                timeout=timeout_config,
            )

            elapsed = (time.perf_counter() - start) * 1000

            if resp.status_code >= 400:
                text = resp.text
                error = FastHTTPBadStatusError(
                    message=f"HTTP {resp.status_code}",
                    url=route.url,
                    method=route.method,
                    status_code=resp.status_code,
                    response_body=text,
                )
                error.log()

                if self.middleware_manager:
                    await self.middleware_manager.process_on_error(
                        error, route, config
                    )

                return None

            text = resp.text

            log_success(route.url, route.method, resp.status_code, elapsed)

            response = Response(
                status=resp.status_code,
                text=text,
                headers=dict(resp.headers),
                method=route.method,
                req_headers=config.get("headers"),
                query=route.params,
                req_json=route.json,
                req_data=route.data,
            )

            if self.middleware_manager:
                response = await self.middleware_manager.process_after_response(
                    response, route, config
                )

            handler_result = await route.handler(response)
            if isinstance(handler_result, Response):
                return handler_result
            if isinstance(handler_result, str):
                response.text = handler_result

            response._handler_result = handler_result
            return response

        except httpx.ConnectError as e:
            error = FastHTTPConnectionError(
                message=str(e) or "Connection failed",
                url=route.url,
                method=route.method,
            )
            error.log()

            if self.middleware_manager:
                await self.middleware_manager.process_on_error(error, route, config)

            return None

        except httpx.TimeoutException as e:
            timeout = config.get("timeout", "default")
            error = FastHTTPTimeoutError(
                message=str(e) or "Request timed out",
                url=route.url,
                method=route.method,
                timeout=timeout,
            )
            error.log()

            if self.middleware_manager:
                await self.middleware_manager.process_on_error(error, route, config)

            return None

        except Exception as e:
            error = FastHTTPRequestError(
                message=str(e) or "Unknown error",
                url=route.url,
                method=route.method,
            )
            error.log()

            if self.middleware_manager:
                await self.middleware_manager.process_on_error(error, route, config)

            return None

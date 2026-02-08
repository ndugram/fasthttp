import asyncio
import time

import aiohttp

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

    This class manages low-level request execution using aiohttp,
    applies per-method request configuration (headers, timeout, redirects),
    logs request lifecycle events, and returns normalized Response objects.
    """

    def __init__(self, request_configs: dict, logger, middleware_manager=None) -> None:
        self.request_configs = request_configs
        self.logger = logger
        self.middleware_manager = middleware_manager

    async def send(
        self, session: aiohttp.ClientSession, route: Route
    ) -> Response | None:
        """
        Send a single HTTP request based on a Route definition.

        This method:
        - Applies request configuration based on HTTP method
        - Executes before_request middleware hooks
        - Sends the request using an existing aiohttp ClientSession
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

        if self.middleware_manager:
            config = await self.middleware_manager.process_before_request(route, config)

        self.logger.debug(
            "→ %s %s | headers=%s",
            route.method,
            route.url,
            config.get("headers"),
        )

        start = time.perf_counter()

        try:
            async with session.request(
                method=route.method,
                url=route.url,
                headers=config.get("headers"),
                params=route.params,
                json=route.json,
                data=route.data,
                timeout=config.get("timeout"),
            ) as resp:
                elapsed = (time.perf_counter() - start) * 1000

                if resp.status >= 400:
                    text = await resp.text()
                    error = FastHTTPBadStatusError(
                        message=f"HTTP {resp.status}",
                        url=route.url,
                        method=route.method,
                        status_code=resp.status,
                        response_body=text,
                    )
                    error.log()

                    if self.middleware_manager:
                        await self.middleware_manager.process_on_error(
                            error, route, config
                        )

                    return None

                text = await resp.text()

                log_success(route.url, route.method, resp.status, elapsed)

                response = Response(
                    status=resp.status,
                    text=text,
                    headers=dict(resp.headers),
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

        except aiohttp.ClientConnectorError as e:
            error = FastHTTPConnectionError(
                message=str(e) or "Connection failed",
                url=route.url,
                method=route.method,
            )
            error.log()

            if self.middleware_manager:
                await self.middleware_manager.process_on_error(error, route, config)

            return None

        except asyncio.TimeoutError as e:
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

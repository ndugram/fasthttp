import asyncio
import time

import aiohttp

from fasthttp.response import Response
from fasthttp.routing import Route


class HTTPClient:
    """
    HTTP client responsible for sending HTTP requests.

    This class manages low-level request execution using aiohttp,
    applies per-method request configuration (headers, timeout, redirects),
    logs request lifecycle events, and returns normalized Response objects.
    """
    def __init__(self, request_configs: dict, logger) -> None:
        self.request_configs = request_configs
        self.logger = logger

    async def send(self, session: aiohttp.ClientSession, route: Route) -> Response | None:
        """
        Send a single HTTP request based on a Route definition.

        This method:
        - Applies request configuration based on HTTP method
        - Sends the request using an existing aiohttp ClientSession
        - Measures request execution time
        - Logs outgoing requests and incoming responses
        - Executes the route handler with the Response object

        Returns:
        - Response instance if the request was successful
        - Modified Response if the handler returned a string or Response
        - None if a connection or timeout error occurred
        """
        config = self.request_configs.get(route.method, {})

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
                text = await resp.text()

                self.logger.info(
                    "← %s %s [%s] %.2fms",
                    route.method,
                    route.url,
                    resp.status,
                    elapsed,
                )

                response = Response(
                    status=resp.status,
                    text=text,
                    headers=dict(resp.headers),
                )

                handler_result = await route.handler(response)
                if isinstance(handler_result, Response):
                    return handler_result
                if isinstance(handler_result, str):
                    response.text = handler_result

                response._handler_result = handler_result
                return response

        except (aiohttp.ClientConnectorError, asyncio.TimeoutError):
            return None

        except Exception:
            return None

import asyncio
import time
from collections.abc import Callable
from typing import Annotated, Literal, get_args, get_origin

import aiohttp
from annotated_doc import Doc
from pydantic import BaseModel

from .client import HTTPClient
from .logging import setup_logger
from .middleware import BaseMiddleware, MiddlewareManager
from .routing import Route
from .types import RequestsOptinal


class FastHTTP:
    """
    FastHTTP application entry point.

    FastHTTP is a lightweight asynchronous HTTP client framework
    built on top of aiohttp. It provides a clean decorator-based API
    for defining HTTP requests and handling responses, similar to
    web frameworks like FastAPI, but for outgoing requests.

    The application manages:
    - Request routing via decorators (GET, POST, PUT, PATCH, DELETE)
    - Per-method default request configuration
    - Async request execution
    - Structured and colorized logging
    - Unified Response handling

    Example:
    ```python
        from fasthttp import FastHTTP
        from fasthttp.response import Response

        app = FastHTTP()

        @app.get(url="https://httpbin.org/get")
        async def get_data(resp: Response):
            return resp.json()

        if __name__ == "__main__":
            app.run()
    ```

    """

    def __init__(
        self,
        *,
        debug: Annotated[
            bool,
            Doc(
                """
                Enable debug mode.

                When enabled, FastHTTP will print datailed
                tracebacks and requests/response logs.
                """
            ),
        ] = False,
        middleware: Annotated[
            list[BaseMiddleware] | BaseMiddleware | None,
            Doc(
                """
                Middleware to apply to all requests.

                Can be a single middleware instance or a list of middleware instances.
                Middleware will be executed in the order they are provided.
                """
            ),
        ] = None,
        get_request: (
            Annotated[
                RequestsOptinal,
                Doc(
                    """
                Default configuration for GET requests.

                Allows setting headers, timeout and other request-level
                options that will be applied to all GET requests
                """
                ),
            ]
            | None
        ) = None,
        post_request: (
            Annotated[
                RequestsOptinal,
                Doc(
                    """
                Default configuration for POST requests.

                Used to define headers, timeout and other options

                applied to all POST requests.
                """
                ),
            ]
            | None
        ) = None,
        put_request: (
            Annotated[
                RequestsOptinal,
                Doc(
                    """
                Default configuration for PUT requests.

                Controls request headers, timeout and other

                options for PUT requests.
                """
                ),
            ]
            | None
        ) = None,
        patch_request: (
            Annotated[
                RequestsOptinal,
                Doc(
                    """
               # Create the app

               Default configuration for PATCH requests.

               Used to configure headers, timeout and
               other PATCH-specific options.
                """
                ),
            ]
            | None
        ) = None,
        delete_request: (
            Annotated[
                RequestsOptinal,
                Doc(
                    """
                Default configuration for DELETE requests.

                Allows defining haders, timeout,
                and other options for DELETE requests.
                """
                ),
            ]
            | None
        ) = None,
    ) -> None:
        self.logger = setup_logger(debug=debug)
        self.routes: list[Route] = []

        if middleware is None:
            normalized_middleware = []
        elif isinstance(middleware, list):
            normalized_middleware = middleware
        else:
            normalized_middleware = [middleware]

        self.middleware_manager = MiddlewareManager(normalized_middleware)

        self.request_configs = {
            "GET": get_request or {},
            "POST": post_request or {},
            "PUT": put_request or {},
            "PATCH": patch_request or {},
            "DELETE": delete_request or {},
        }

        self.client = HTTPClient(
            self.request_configs, self.logger, self.middleware_manager
        )

    def _add_route(
        self,
        *,
        method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"],
        url: str,
        params: dict | None = None,
        json: dict | None = None,
        data: object | None = None,
        response_model: type[BaseModel] | None = None,
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
        def decorator(func: Callable[..., object]) -> Callable[..., object]:
            self.routes.append(
                Route(
                    method=method,
                    url=url,
                    handler=func,
                    params=params,
                    json=json,
                    data=data,
                    response_model=response_model,
                )
            )
            self.logger.debug("Registered route: %s %s", method, url)
            return func

        return decorator

    def get(
        self,
        *,
        url: str,
        params: dict | None = None,
        response_model: type[BaseModel] | None = None,
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
        return self._add_route(
            method="GET", url=url, params=params, response_model=response_model
        )

    def post(
        self,
        *,
        url: str,
        json: dict | None = None,
        data: object | None = None,
        response_model: type[BaseModel] | None = None,
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
        return self._add_route(
            method="POST", url=url, json=json, data=data, response_model=response_model
        )

    def put(
        self,
        *,
        url: str,
        json: dict | None = None,
        data: object | None = None,
        response_model: type[BaseModel] | None = None,
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
        return self._add_route(
            method="PUT", url=url, json=json, data=data, response_model=response_model
        )

    def patch(
        self,
        *,
        url: str,
        json: dict | None = None,
        data: object | None = None,
        response_model: type[BaseModel] | None = None,
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
        return self._add_route(
            method="PATCH", url=url, json=json, data=data, response_model=response_model
        )

    def delete(
        self,
        *,
        url: str,
        json: dict | None = None,
        data: object | None = None,
        response_model: type[BaseModel] | None = None,
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
        return self._add_route(
            method="DELETE",
            url=url,
            json=json,
            data=data,
            response_model=response_model,
        )

    async def _run(self) -> None:
        total = len(self.routes)

        self.logger.info("Sending %d requests", total)
        start_all = time.perf_counter()

        async with aiohttp.ClientSession() as session:
            for route in self.routes:
                start = time.perf_counter()

                result = await self.client.send(session, route)
                elapsed = (time.perf_counter() - start) * 1000

                if result and isinstance(result.status, int):
                    self.logger.info(
                        "✔️ %-6s %-30s %s %6.2fms",
                        route.method,
                        route.url,
                        result.status,
                        elapsed,
                    )

                    handler_result = getattr(result, "_handler_result", None)
                    if route.response_model and handler_result is not None:
                        if get_origin(route.response_model) is list:
                            item_model = get_args(route.response_model)[0]
                            handler_result = [
                                item_model.model_validate(item)
                                for item in handler_result
                            ]
                        else:
                            handler_result = route.response_model.model_validate(
                                handler_result
                            )

                        self.logger.debug("[RESULT] %s", handler_result)
                    elif result.text:
                        self.logger.debug("[RESULT] %s", result.text)
                else:
                    self.logger.error(
                        "✖️ %-6s %-30s ERR %6.2fms",
                        route.method,
                        route.url,
                        elapsed,
                    )

                await asyncio.sleep(0.5)

        total_time = time.perf_counter() - start_all
        self.logger.info("Done in %.2fs", total_time)

    def run(self) -> None:
        self.logger.info("FastHTTP started")
        try:
            asyncio.run(self._run())
        except aiohttp.ClientConnectionError as e:
            self.logger.error("Connection error: %s", e)
        except KeyboardInterrupt:
            self.logger.warning("Interrupted by user")

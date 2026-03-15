from __future__ import annotations

import asyncio
import inspect
import time
from typing import TYPE_CHECKING, Annotated, Literal, get_args, get_origin

import httpx
from annotated_doc import Doc

from .client import HTTPClient
from .graphql.client import create_graphql_client
from .logging import setup_logger
from .middleware import BaseMiddleware, MiddlewareManager
from .routing import Route
from .security import Security

if TYPE_CHECKING:
    from collections.abc import Callable

    from pydantic import BaseModel

    from .response import Response
    from .types import RequestsOptinal


class FastHTTP:
    """
    FastHTTP application entry point.

    FastHTTP is a lightweight asynchronous HTTP client framework
    built on top of httpx. It provides a clean decorator-based API
    for defining HTTP requests and handling responses, similar to
    web frameworks like FastAPI, but for outgoing requests.

    The application manages:
    - Request routing via decorators (GET, POST, PUT, PATCH, DELETE)
    - Per-method default request configuration
    - Async request execution
    - Structured and colorized logging
    - Unified Response handling
    - HTTP/2 support (optional)
    - Middleware system
    - Rate limiting

    Example:
    ```python
        from fasthttp import FastHTTP
        from fasthttp.response import Response

        app = FastHTTP(http2=True)

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

                Can be a single middleware instance or a list of middleware.
                Middleware will be executed in the order they are provided.
                """
            ),
        ] = None,
        http2: Annotated[
            bool,
            Doc(
                """
                Enable HTTP/2 support.

                When enabled, FastHTTP will use HTTP/2 for requests
                to servers that support it. Requires httpx[http2] package.
                """
            ),
        ] = False,
        get_request: (
            Annotated[
                RequestsOptinal | None,
                Doc(
                    """
                Default configuration for GET requests.

                Allows setting headers, timeout and other request-level
                options that will be applied to all GET requests
                """
                ),
            ]
        ) = None,
        post_request: (
            Annotated[
                RequestsOptinal | None,
                Doc(
                    """
                Default configuration for POST requests.

                Used to define headers, timeout and other options

                applied to all POST requests.
                """
                ),
            ]
        ) = None,
        put_request: (
            Annotated[
                RequestsOptinal | None,
                Doc(
                    """
                Default configuration for PUT requests.

                Controls request headers, timeout and other

                options for PUT requests.
                """
                ),
            ]
        ) = None,
        patch_request: (
            Annotated[
                RequestsOptinal | None,
                Doc(
                    """
               # Create the app

               Default configuration for PATCH requests.

               Used to configure headers, timeout and
               other PATCH-specific options.
                """
                ),
            ]
        ) = None,
        delete_request: (
            Annotated[
                RequestsOptinal | None,
                Doc(
                    """
                Default configuration for DELETE requests.

                Allows defining haders, timeout,
                and other options for DELETE requests.
                """
                ),
            ]
        ) = None,
        security: Annotated[
            bool,
            Doc(
                """
                Enable built-in security features.

                When enabled (default), FastHTTP automatically against:
                - SSRF attacks (blocking localhost and private IPs)
                - Secret leakage in logs
                - Circuit breaker for failed hosts
                - Large response limits
                - Dangerous redirects
                - Request timeouts

                Set to False to disable all security features.
                """
            ),
        ] = True,
        lifespan: Annotated[
            Callable[[FastHTTP], object] | None,
            Doc(
                """
                Lifespan context manager for startup and shutdown logic.

                Allows running code before and after all requests.
                Useful for initializing resources (tokens, connections)
                and cleaning up after execution.

                Example:
                ```python
                from contextlib import asynccontextmanager
                from fasthttp import FastHTTP

                @asynccontextmanager
                async def lifespan(app: FastHTTP):
                    # Startup
                    print("Starting up...")
                    app.auth_token = await load_token()
                    yield
                    # Shutdown
                    print("Shutting down...")

                app = FastHTTP(lifespan=lifespan)
                ```
                """
            ),
        ] = None,
    ) -> None:
        self.logger = setup_logger(debug=debug)
        self.routes: list[Route] = []
        self.http2_enabled = http2
        self.lifespan = lifespan

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

        self.security_enabled = security
        self.security = Security() if security else None
        self.client = HTTPClient(
            self.request_configs,
            self.logger,
            self.middleware_manager,
            self.security
        )

    def _check_annotated_parameters(
        self,
        *,
        func: Annotated[
            Callable,
            Doc(
                """
                Validate that all function parameters have type annotations.

                This method checks if all parameters of the provided function
                have explicit type annotations. Type annotations are required
                for proper type checking and documentation generation.

                If any parameter is missing a type annotation, a TypeError
                is raised with a descriptive message.

                Args:
                    func: The function to validate.

                Raises:
                    TypeError: If any parameter lacks a type annotation.

                Example:
                    ```python
                    @app.get(url="https://api.example.com/data")
                    async def get_data(resp: Response) -> dict:
                        return resp.json()
                    ```
                """
            ),
        ]
    ) -> None:
        sig = inspect.signature(func)

        for name, param in sig.parameters.items():
            if param.annotation is inspect.Parameter.empty:
                msg = (
                    f"Parameter '{name}' in function '{func.__name__}'"
                    "must have a type annotation"
                )
                raise TypeError(
                    msg
                )

    def _check_annotated_func(
        self,
        *,
        func: Annotated[
            Callable,
            Doc(
                """
                Validate that the function has a return type annotation.

                This method checks if the provided function has an explicit
                return type annotation. Return type annotations are required
                for proper type checking and documentation generation.

                If the return type annotation is missing, a TypeError
                is raised with a descriptive message.

                Args:
                    func: The function to validate.

                Raises:
                    TypeError: If the return type is not annotated.

                Example:
                    ```python
                    @app.get(url="https://api.example.com/data")
                    async def get_data(resp: Response) -> dict:
                        return resp.json()
                    ```
                """
            ),
        ]
    ) -> None:
        sig = inspect.signature(func)

        if sig.return_annotation is inspect.Signature.empty:
            msg = (
                f"Function '{func.__name__}' must explicitly"
                "define return type annotation"
            )
            raise TypeError(
                msg
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
        request_model: type[BaseModel] | None = None,
        tags: list[str] | None = None,
        dependencies: list | None = None,
        responses: dict[int, dict[Literal["model"], type[BaseModel]]] | None = None,
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
        def decorator(func: Callable[..., object]) -> Callable[..., object]:
            self._check_annotated_parameters(func=func)
            self._check_annotated_func(func=func)
            self.routes.append(
                Route(
                    method=method,
                    url=url,
                    handler=func,
                    params=params,
                    json=json,
                    data=data,
                    response_model=response_model,
                    request_model=request_model,
                    tags=tags,
                    dependencies=dependencies,
                    responses=responses,
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
        request_model: type[BaseModel] | None = None,
        tags: list[str] | None = None,
        dependencies: list | None = None,
        responses: dict[int, dict[Literal["model"], type[BaseModel]]] | None = None,
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
        return self._add_route(
            method="GET",
            url=url,
            params=params,
            response_model=response_model,
            request_model=request_model,
            tags=tags,
            dependencies=dependencies,
            responses=responses,
        )

    def post(
        self,
        *,
        url: str,
        json: dict | None = None,
        data: object | None = None,
        response_model: type[BaseModel] | None = None,
        request_model: type[BaseModel] | None = None,
        tags: list[str] | None = None,
        dependencies: list | None = None,
        responses: dict[int, dict[Literal["model"], type[BaseModel]]] | None = None,
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
        return self._add_route(
            method="POST",
            url=url,
            json=json,
            data=data,
            response_model=response_model,
            request_model=request_model,
            tags=tags,
            dependencies=dependencies,
            responses=responses,
        )

    def put(
        self,
        *,
        url: str,
        json: dict | None = None,
        data: object | None = None,
        response_model: type[BaseModel] | None = None,
        request_model: type[BaseModel] | None = None,
        tags: list[str] | None = None,
        dependencies: list | None = None,
        responses: dict[int, dict[Literal["model"], type[BaseModel]]] | None = None,
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
        return self._add_route(
            method="PUT",
            url=url,
            json=json,
            data=data,
            response_model=response_model,
            request_model=request_model,
            tags=tags,
            dependencies=dependencies,
            responses=responses,
        )

    def patch(
        self,
        *,
        url: str,
        json: dict | None = None,
        data: object | None = None,
        response_model: type[BaseModel] | None = None,
        request_model: type[BaseModel] | None = None,
        tags: list[str] | None = None,
        dependencies: list | None = None,
        responses: dict[int, dict[Literal["model"], type[BaseModel]]] | None = None,
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
        return self._add_route(
            method="PATCH",
            url=url,
            json=json,
            data=data,
            response_model=response_model,
            request_model=request_model,
            tags=tags,
            dependencies=dependencies,
            responses=responses,
        )

    def delete(
        self,
        *,
        url: str,
        json: dict | None = None,
        data: object | None = None,
        response_model: type[BaseModel] | None = None,
        request_model: type[BaseModel] | None = None,
        tags: list[str] | None = None,
        dependencies: list | None = None,
        responses: dict[int, dict[Literal["model"], type[BaseModel]]] | None = None,
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
        return self._add_route(
            method="DELETE",
            url=url,
            json=json,
            data=data,
            response_model=response_model,
            request_model=request_model,
            tags=tags,
            dependencies=dependencies,
            responses=responses,
        )

    def graphql(
        self,
        *,
        url: Annotated[
            str,
            Doc(
                """
                GraphQL endpoint URL.

                The URL of the GraphQL server to send queries to.
                """
            ),
        ],
        operation_type: Annotated[
            Literal["query", "mutation"],
            Doc(
                """
                Type of GraphQL operation.

                Use "query" for read operations and
                "mutation" for write operations.
                """
            ),
        ] = "query",
        headers: Annotated[
            dict[str, str] | None,
            Doc(
                """
                Additional headers for GraphQL requests.

                Common headers include Authorization tokens.
                """
            ),
        ] = None,
        timeout: Annotated[
            float | None,
            Doc(
                """
                Request timeout in seconds.
                """
            ),
        ] = 30.0,
        tags: Annotated[
            list[str] | None,
            Doc(
                """
                Tags for grouping and filtering requests.
                """
            ),
        ] = None,
        response_model: Annotated[
            type[BaseModel] | None,
            Doc(
                """
                Optional Pydantic model for validating response data.

                If provided, the GraphQL response data will be
                validated before being returned.
                """
            ),
        ] = None,
        dependencies: Annotated[
            list | None,
            Doc(
                """
                List of dependencies to execute before the request.

                Dependencies are functions that modify the request
                config before the request is sent.
                """
            ),
        ] = None,
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
        """
        Decorator for GraphQL queries and mutations.

        Allows defining GraphQL operations using the same
        decorator-based API as other HTTP methods.

        Example:
        ```python
            from fasthttp import FastHTTP
            from fasthttp.response import Response

            app = FastHTTP()

            @app.graphql(url="https://api.example.com/graphql")
            async def get_user(resp: Response) -> dict:
                return {"query": "{ user(id: 1) { name } }"}
        ```
        """
        def decorator(func: Callable[..., object]) -> Callable[..., object]:
            self._check_annotated_parameters(func=func)
            self._check_annotated_func(func=func)

            async def graphql_handler(response: Response) -> object:
                from inspect import iscoroutinefunction

                if iscoroutinefunction(func):
                    handler_result = await func(response)
                else:
                    handler_result = func(response)

                if isinstance(handler_result, dict):
                    query = handler_result.get("query")
                    variables = handler_result.get("variables")
                    operation_name = handler_result.get("operation_name")
                else:
                    query = handler_result
                    variables = None
                    operation_name = None

                client = create_graphql_client(
                    url=url,
                    headers=headers,
                    timeout=timeout,
                )

                if operation_type == "mutation":
                    result = await client.mutation(
                        mutation=query,
                        variables=variables,
                        operation_name=operation_name,
                    )
                else:
                    result = await client.query(
                        query=query,
                        variables=variables,
                        operation_name=operation_name,
                    )

                return result.data

            self.routes.append(
                Route(
                    method="POST",
                    url=url,
                    handler=graphql_handler,
                    tags=tags,
                    skip_request=True,
                    response_model=response_model,
                    dependencies=dependencies,
                )
            )
            self.logger.debug(
                "Registered GraphQL %s: %s",
                operation_type,
                url
            )
            return func

        return decorator

    def _log_result(
        self,
        route: Route,
        elapsed: float,
        result: Response | None
    ) -> None:
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
            elif handler_result is not None:
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

    async def _run(self, routes: list[Route] | None = None) -> None:
        routes = routes or self.routes
        total = len(routes)

        self.logger.info("Sending %d requests", total)
        if self.http2_enabled:
            self.logger.info("HTTP/2 enabled")

        start_all = time.perf_counter()

        async with httpx.AsyncClient(http2=self.http2_enabled) as client:
            if total > 1:
                tasks = [
                    self._run_route(client, route)
                    for route in routes
                ]
                results = await asyncio.gather(*tasks)

                for route, elapsed, result in results:
                    self._log_result(route, elapsed, result)
            else:
                route, elapsed, result = await self._run_route(
                    client, routes[0]
                )
                self._log_result(route, elapsed, result)

        total_time = time.perf_counter() - start_all
        self.logger.info("Done in %.2fs", total_time)

    async def _run_with_lifespan(self, routes: list[Route]) -> None:
        async with self.lifespan(self):  # type: ignore
            await self._run(routes)

    async def _run_route(
        self, client: httpx.AsyncClient, route: Route
    ) -> tuple[Route, float, Response | None]:
        start = time.perf_counter()
        result = await self.client.send(client, route)
        elapsed = (time.perf_counter() - start) * 1000
        return route, elapsed, result

    def run(self, tags: list[str] | None = None) -> None:
        """
        Run all registered HTTP requests.

        Executes all routes sequentially or in parallel
        and logs the results.

        Args:
            tags: Optional list of tags to filter which routes to run.
                  If provided, only routes with matching tags will be executed.
                  If None, all routes will be executed.
        """
        self.logger.info("FastHTTP started")

        routes_to_run = self.routes
        if tags:
            routes_to_run = [
                route for route in self.routes
                if any(tag in route.tags for tag in tags)
            ]
            self.logger.info(
                "Running %d routes with tags: %s",
                len(routes_to_run), tags
            )

        if not routes_to_run:
            self.logger.warning("No routes to run")
            return

        try:
            if self.lifespan:
                asyncio.run(self._run_with_lifespan(routes_to_run))
            else:
                asyncio.run(self._run(routes_to_run))
        except ImportError as e:
            if "http2" in str(e).lower():
                self.logger.error(
                    "HTTP/2 support requires additional dependencies. "
                    "Install with: pip install fasthttp-client[http2]"
                )
            else:
                raise
        except httpx.ConnectError as e:
            self.logger.error("Connection error: %s", e)
        except KeyboardInterrupt:
            self.logger.warning("Interrupted by user")

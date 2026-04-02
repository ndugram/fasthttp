from __future__ import annotations

import asyncio
import json
import secrets
import time
import uuid
from typing import TYPE_CHECKING, Annotated, Any, Literal, get_args, get_origin

import httpx
from annotated_doc import Doc

from .client import HTTPClient
from .graphql.client import create_graphql_client
from .helpers.route_inspect import (
    check_annotated_parameters,
    check_annotated_return,
    validate_handler,
)
from .helpers.routing import apply_base_url, check_https_url
from .logging import setup_logger
from .middleware import BaseMiddleware, MiddlewareManager
from .openapi.generator import generate_openapi_schema
from .openapi.swagger import get_not_found_html, get_swagger_html
from .openapi.urls import build_docs_urls
from .routing import Route, Router
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
        proxy: Annotated[
            str | None,
            Doc(
                """
                Proxy server to use for requests.

                Supports:
                - HTTP proxy: "http://proxy.example.com:8080"
                - HTTPS proxy: "https://proxy.example.com:8080"
                - With authentication: "http://user:pass@proxy.example.com:8080"

                Example:
                    ```python
                    app = FastHTTP(proxy="http://proxy.example.com:8080")
                    ```
                """
            ),
        ] = None,
        secret_key: Annotated[
            bytes | None,
            Doc(
                """
                Secret key for request signing.

                If not provided, a key will be automatically generated.
                The key is used for HMAC-SHA256 signing of outgoing requests.
                """
            ),
        ] = None,
        generate_startup_uuid: Annotated[
            bool,
            Doc(
                """
                Whether to generate a random UUID on application startup.
                The generated UUID will be stored in `app.startup_uuid`.
                **Example**
                ```python
                from fashttp import FastHTTP
                app = FastHTTP(generate_startup_uuid=True)
                print(app.startup_uuid)  # UUID('...')
                ```
                """
            ),
        ] = False,
        startup_uuid_version: Annotated[
            str,
            Doc(
                """
                The version of UUID to generate on startup if `generate_startup_uuid` is True.
                Supported versions: 'v4' (random UUID), 'v7' (time-based UUID with random component, requires Python 3.12+).
                **Example**
                ```python
                from fashttp import FastHTTP
                app = FastHTTP(generate_startup_uuid=True, startup_uuid_version="v7")
                ```
                """
            ),
        ] = "v4",
        base_url: Annotated[
            str | None,
            Doc(
                """
                Default base URL for requests.

                This value is used by:
                - Decorators (`@app.get`, `@app.post`, etc.) with relative paths
                - GraphQL (`@app.graphql`) with relative paths
                - `include_router()` when the router tree contains relative URLs

                Example:
                ```python
                app = FastHTTP(base_url="https://api.example.com")

                @app.get("/users")  # → https://api.example.com/users
                ```
                """
            ),
        ] = None,
        docs_base_url: Annotated[
            str,
            Doc(
                """
                Default URL prefix for Swagger/OpenAPI endpoints.

                This value is used by `web_run()` when no explicit
                `base_url` is provided for documentation routes.

                Example:
                ```python
                app = FastHTTP(docs_base_url="/api")
                ```
                """
            ),
        ] = "",
    ) -> None:
        self.logger = setup_logger(debug=debug)
        self.routes: list[Route] = []
        self.http2_enabled = http2
        self.lifespan = lifespan
        self.proxy = proxy
        self.base_url = base_url
        self.docs_base_url = docs_base_url
        self.generate_startup_uuid = generate_startup_uuid
        self.startup_uuid_version = startup_uuid_version


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
        self.secret_key = secret_key or secrets.token_bytes(32)
        self.security = Security(secret_key=self.secret_key) if security else None
        self.startup_uuid = None
        if self.generate_startup_uuid and self.startup_uuid_version == "v4":
            self.startup_uuid = str(uuid.uuid4())

        self.client = HTTPClient(
            self.request_configs,
            self.logger,
            self.middleware_manager,
            self.security,
            self.startup_uuid
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
        check_annotated_parameters(func=func)

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
        check_annotated_return(func=func)

    def _check_https_url(
        self,
        *,
        url: str
    ) -> str:
        """
        Ensure URL has a valid scheme (http:// or https://).

        If no scheme is provided, https:// is added by default.
        This prevents errors when users forget to include the protocol.

        Args:
            url: The URL to check and normalize.

        Returns:
            URL with a valid scheme (https:// if not specified).

        Example:
            >>> _check_https_url("api.example.com")
            'https://api.example.com'
            >>> _check_https_url("http://api.example.com")
            'http://api.example.com'
            >>> _check_https_url("https://api.example.com")
            'https://api.example.com'
        """
        return check_https_url(url=url)

    def _resolve_url(self, url: str) -> str:
        return apply_base_url(url=url, base_url=self.base_url)

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
            validate_handler(func=func)

            self.routes.append(
                Route(
                    method=method,
                    url=self._resolve_url(url),
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

    def include_router(
        self,
        router: Annotated[
            Router,
            Doc(
                """
                Router instance to include into the application.

                The router can define its own routes, nested routers,
                shared tags, dependencies, prefix, and base_url.
                """
            ),
        ],
        *,
        prefix: Annotated[
            str,
            Doc(
                """
                Optional prefix added before the router prefix.

                Useful when the same router should be mounted under
                different path segments in different applications.
                """
            ),
        ] = "",
        tags: Annotated[
            list[str] | None,
            Doc(
                """
                Optional tags prepended before router tags.

                These tags will be inherited by all routes that come
                from the included router tree.
                """
            ),
        ] = None,
        dependencies: Annotated[
            list | None,
            Doc(
                """
                Optional dependencies prepended before router dependencies.

                They will run before dependencies declared on the router
                and on its individual routes.
                """
            ),
        ] = None,
        base_url: Annotated[
            str | None,
            Doc(
                """
                Optional base URL override for the included router tree.

                This is useful when a router defines relative paths such
                as `/users` and the application should provide the host.
                """
            ),
        ] = None,
    ) -> None:
        """
        Include a Router into the FastHTTP application.

        Included routers are resolved into concrete Route objects and then
        appended to `self.routes`.

        Example:
            ```python
            from fasthttp import FastHTTP, Router

            app = FastHTTP()
            router = Router(base_url="https://api.example.com", prefix="/v1")

            app.include_router(router, prefix="/public")
            ```

        Args:
            router: Router instance to include.
            prefix: Prefix added before the router prefix.
            tags: Tags prepended before router tags.
            dependencies: Dependencies prepended before router dependencies.
            base_url: Base URL override for the included router tree.
                If not provided, `FastHTTP.base_url` will be used.
        """
        resolved_base_url = base_url if base_url is not None else self.base_url
        routes = router.build_routes(
            base_url=resolved_base_url,
            prefix=prefix,
            tags=tags,
            dependencies=dependencies,
        )
        self.routes.extend(routes)
        self.logger.debug("Included router: %d routes", len(routes))

    def get(
        self,
        url: str,
        *,
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
        url: str,
        *,
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
        url: str,
        *,
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
        url: str,
        *,
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
        url: str,
        *,
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
        url: Annotated[
            str,
            Doc(
                """
                GraphQL endpoint URL.

                The URL of the GraphQL server to send queries to.
                """
            ),
        ],
        *,
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
            validate_handler(func=func)

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
                    url=self._resolve_url(url),
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
        if self.proxy:
            self.logger.info("Proxy enabled: %s", self.proxy)

        start_all = time.perf_counter()

        async with httpx.AsyncClient(
            http2=self.http2_enabled,
            proxy=self.proxy,
        ) as client:
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

    def web_run(
        self,
        *,
        host: Annotated[
            str,
            Doc(
                """
                Host to bind the ASGI server to.

                Default is "127.0.0.1".
                """
            ),
        ] = "127.0.0.1",
        port: Annotated[
            int,
            Doc(
                """
                Port to bind the ASGI server to.

                Default is 8000.
                """,
            ),
        ] = 8000,
        base_url: Annotated[
            str | None,
            Doc(
                """
                Optional URL prefix for Swagger/OpenAPI endpoints.

                For example, with `base_url="/api"`, the docs will be served at
                `/api/docs`, `/api/openapi.json`, and `/api/request`.
                """
            ),
        ] = None,
    ) -> None:
        """
        Run the FastHTTP application as an ASGI server with Swagger UI.

        This method starts a local HTTP server that serves:
        - {base_url}/docs - Swagger UI interface
        - {base_url}/openapi.json - OpenAPI schema
        - {base_url}/request - Execute HTTP requests from Swagger UI

        The server allows you to test and execute HTTP requests
        through the Swagger UI interface.

        Example:
            ```python
            from fasthttp import FastHTTP

            app = FastHTTP()

            @app.get("https://google.com")
            async def index(resp):
                return resp.status

            app.web_run()
            ```

        Args:
            host: Host to bind to. Default is "127.0.0.1".
            port: Port to bind to. Default is 8000.
            base_url: Optional prefix for documentation endpoints.
                If not provided, `FastHTTP.docs_base_url` will be used.
        """
        self.logger.info("FastHTTP started")

        docs_base_url = (
            base_url if base_url is not None else self.docs_base_url
        )
        app = ASGIApp(self, base_url=docs_base_url)

        server_base_url = f"http://{host}:{port}"
        docs_urls = build_docs_urls(docs_base_url)

        print(f"\n\033[92mfasthttp\033[0m running on \033[94m{server_base_url}\033[0m")
        print(
            f"\033[93mdocs\033[0m: "
            f"\033[94m{server_base_url}{docs_urls['docs_url']}\033[0m\n"
        )

        try:
            import uvicorn

            uvicorn.run(app, host=host, port=port, log_level="info")
        except ImportError:
            self.logger.warning(
                "uvicorn not found. Using built-in ASGI server. "
                "Install uvicorn for better performance: pip install uvicorn"
            )
            asyncio.run(self._run_asgi_server(app, host, port))

    async def _run_asgi_server(
        self,
        app: ASGIApp,
        host: str,
        port: int,
    ) -> None:
        server = await asyncio.start_server(
            app.handle_request,
            host,
            port,
        )

        async with server:
            await server.serve_forever()


class ASGIApp:
    """
    ASGI application for FastHTTP.

    This class provides ASGI compatibility for FastHTTP,
    enabling it to serve Swagger UI and handle HTTP requests.
    """

    def __init__(
        self,
        app: Annotated[
            FastHTTP,
            Doc("FastHTTP application instance"),
        ],
        *,
        base_url: Annotated[
            str,
            Doc("Optional docs base URL prefix"),
        ] = "",
    ) -> None:
        self.fasthttp = app
        self.docs_urls = build_docs_urls(base_url)

    async def __call__(
        self,
        scope: dict,
        receive: Callable[..., Any],
        send: Callable[..., Any],
    ) -> None:
        await self.handle_request(scope, receive, send)

    async def handle_request(
        self,
        scope: dict,
        receive: Callable[..., Any],
        send: Callable[..., Any],
    ) -> None:
        path = scope.get("path", "/")
        method = scope.get("method", "GET")

        body = b""
        if method in ("POST", "PUT", "PATCH"):
            while True:
                message = await receive()
                if message["type"] == "http.request":
                    body += message.get("body", b"")
                    if not message.get("more_body"):
                        break

        if path == self.docs_urls["docs_url"] or path.startswith(f"{self.docs_urls['docs_url']}/"):
            await self._send_html(
                send,
                get_swagger_html(
                    openapi_url=self.docs_urls["openapi_url"],
                    request_url=self.docs_urls["request_url"],
                ),
            )
        elif path == self.docs_urls["openapi_url"]:
            schema = generate_openapi_schema(
                self.fasthttp,
                server_url=self.docs_urls["request_url"],
            )
            await self._send_json(send, schema)
        elif path == self.docs_urls["request_url"]:
            await self._handle_proxy(send, method, body)
        else:
            await self._send_404(send, path)

    async def _send_html(self, send: Callable[..., Any], html: str) -> None:
        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [[b"content-type", b"text/html; charset=utf-8"]],
        })
        await send({
            "type": "http.response.body",
            "body": html.encode("utf-8"),
        })

    async def _send_json(self, send: Callable[..., Any], data: dict) -> None:
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [[b"content-type", b"application/json; charset=utf-8"]],
        })
        await send({
            "type": "http.response.body",
            "body": json_str.encode("utf-8"),
        })

    async def _send_404(self, send: Callable[..., Any], path: str = "/") -> None:
        html = get_not_found_html(
            docs_url=self.docs_urls["docs_url"],
            openapi_url=self.docs_urls["openapi_url"],
        )
        await send({
            "type": "http.response.start",
            "status": 404,
            "headers": [[b"content-type", b"text/html; charset=utf-8"]],
        })
        await send({
            "type": "http.response.body",
            "body": html.encode("utf-8"),
        })

    async def _handle_proxy(
        self,
        send: Callable[..., Any],
        method: str,
        body: bytes,
    ) -> None:
        try:
            request_data = {}
            if body:
                try:
                    request_data = json.loads(body)
                except json.JSONDecodeError:
                    await self._send_json(send, {"error": "Invalid JSON"})
                    return

            real_method = request_data.get("method", "GET")
            url = request_data.get("url", "")
            headers = request_data.get("headers", {})
            req_body = request_data.get("body")

            if not url:
                await self._send_json(send, {"error": "URL is required"})
                return

            async with httpx.AsyncClient(
                proxy=self.fasthttp.proxy,
            ) as client:
                kwargs: dict[str, Any] = {
                    "method": real_method,
                    "url": url,
                    "headers": headers,
                }

                if req_body and real_method in ("POST", "PUT", "PATCH"):
                    if isinstance(req_body, dict):
                        kwargs["json"] = req_body
                    else:
                        kwargs["content"] = str(req_body)

                response = await client.request(**kwargs)

                result = {
                    "status": response.status_code,
                    "headers": dict(response.headers),
                    "body": response.text,
                }

                try:
                    result["json"] = response.json()
                except Exception:
                    pass

                await self._send_json(send, result)

        except httpx.ConnectError as e:
            await self._send_json(send, {"error": f"Connection error: {e!s}"})
        except httpx.TimeoutException as e:
            await self._send_json(send, {"error": f"Timeout: {e!s}"})
        except Exception as e:
            await self._send_json(send, {"error": f"Request failed: {e!s}"})

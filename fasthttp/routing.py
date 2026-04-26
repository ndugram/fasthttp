from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated, Literal

from annotated_doc import Doc
from pydantic import BaseModel

from .helpers.routing import join_prefix as _join_prefix
from .helpers.routing import resolve_url as _resolve_url
from .helpers.route_inspect import validate_handler


class Route:
    """
    Definition of an HTTP request route.

    A Route binds together an HTTP method, a target URL,
    optional request data, and a response handler function.

    It is used by FastHTTP to send requests and process
    responses in a structured and predictable way.
    """

    def __init__(
        self,
        *,
        method: Annotated[
            Literal["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
            Doc(
                """
                HTTP method for the request.

                Determines how the request will be sent to the server.

                Supported methods are:
                GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS.
                """
            ),
        ],
        url: Annotated[
            str,
            Doc(
                """
                Target URL for the HTTP request.

                Must be a full URL including scheme, host and path
                Example:
                https://api.google.com/
                """
            ),
        ],
        handler: Annotated[
            Callable,
            Doc(
                """
                Response handler function.

                This async function will be called with a Response object
                and can return:
                - str
                - Response
                - None
                """
            ),
        ],
        params: Annotated[
            dict | None,
            Doc(
                """
                Query parameters to be sent with the request.

                The dictionary will be encoded into the URL query string
                and appended to the request URL.
                """
            ),
        ] = None,
        json: Annotated[
            dict | None,
            Doc(
                """
                JSON body to be sent with the request.

                The data will be serialized to JSON and sent with the

                application/json Content-Type header.
                """
            ),
        ] = None,
        data: Annotated[
            object | None,
            Doc(
                """

                Raw request body or form data.

                Can be used to send form-encoded data, plain text,

                binary payloads or any custom request body.
                """
            ),
        ] = None,
        response_model: Annotated[
            type[BaseModel] | None,
            Doc(
                """
                Optional Pydantic model for validating handler results.

                If provided, the handler return value will be
                validated before returning.

                If None, the result is returned unchanged.
                """
            ),
        ] = None,
        request_model: Annotated[
            type[BaseModel] | None,
            Doc(
                """
                Optional Pydantic model for validating request data.

                If provided, the request json/data will be validated
                before sending the request.

                If None, the request data is sent without validation.
                """
            ),
        ] = None,
        tags: Annotated[
            list[str] | None,
            Doc(
                """
                Tags for grouping and filtering requests.

                Tags allow you to organize routes and run only
                specific groups of requests. Useful for running
                subsets of requests in large applications.

                Example:
                    tags=["users"] - route belongs to "users" group
                """
            ),
        ] = None,
        dependencies: Annotated[
            list | None,
            Doc(
                """
                List of dependencies to execute before the request.

                Dependencies are functions that modify the request
                config (headers, params, etc.) before the request
                is sent. Useful for adding auth tokens, logging,
                or other request modifications.

                Example:
                    dependencies=[Depends(add_auth), Depends(add_trace_id)]
                """
            ),
        ] = None,
        skip_request: Annotated[
            bool,
            Doc(
                """
                Skip HTTP request execution.

                When True, the HTTP client will not send a real request.
                The handler is responsible for executing the request
                and returning the result. Used for GraphQL and custom
                protocols.
                """
            ),
        ] = False,
        responses: Annotated[
            dict[int, dict[Literal["model"], type[BaseModel]]] | None,
            Doc(
                """
                Response models for different status codes.

                A dictionary mapping HTTP status codes to Pydantic models
                that will be used to validate error responses.

                Example:
                    responses={
                        404: {"model": Error404},
                        500: {"model": Error500}
                    }

                When the server returns an error status code (4xx, 5xx),
                the response body will be validated against the
                corresponding model.
                """
            ),
        ] = None,
    ) -> None:
        self.method = method
        self.url = url
        self.handler = handler
        self.params = params
        self.json = json
        self.data = data
        self.response_model = response_model
        self.request_model = request_model
        self.tags = tags or []
        self.dependencies = dependencies or []
        self.skip_request = skip_request
        self.responses = responses or {}


@dataclass(frozen=True, slots=True)
class _RouteDef:
    """
    Internal representation of a route defined on Router.

    Stored before URL/prefix/base_url resolution.
    """

    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
    url: str
    handler: Callable[..., object]
    params: dict | None
    json: dict | None
    data: object | None
    response_model: type[BaseModel] | None
    request_model: type[BaseModel] | None
    tags: list[str]
    dependencies: list
    skip_request: bool
    responses: dict[int, dict[Literal["model"], type[BaseModel]]]


@dataclass(frozen=True, slots=True)
class _IncludeDef:
    """
    Internal representation of Router.include_router() call.
    """

    router: Router
    prefix: str
    tags: list[str]
    dependencies: list
    base_url: str | None


class Router:
    """
    Router for grouping and composing routes, similar to FastAPI/APIRouter.

    Router collects route definitions and can be included into a FastHTTP app
    via FastHTTP.include_router(router, ...).

    It supports:
    - base_url (e.g. "https://api.example.com")
    - prefix (e.g. "/v1")
    - tags and dependencies inheritance
    - nested routers via include_router()
    """

    def __init__(
        self,
        *,
        base_url: Annotated[
            str | None,
            Doc(
                """
                Base URL used to resolve relative route paths.

                Example:
                    "https://api.example.com"
                """
            ),
        ] = None,
        prefix: Annotated[
            str,
            Doc(
                """
                Shared path prefix applied to all routes in this router.

                Example:
                    "/v1"
                """
            ),
        ] = "",
        tags: Annotated[
            list[str] | None,
            Doc(
                """
                Shared tags inherited by all routes in this router.

                Useful for grouping related routes such as "users",
                "payments", or "admin".
                """
            ),
        ] = None,
        dependencies: Annotated[
            list | None,
            Doc(
                """
                Shared dependencies inherited by all routes in this router.

                These dependencies will run before route-specific
                dependencies.
                """
            ),
        ] = None,
    ) -> None:
        """
        Create a new Router.

        Router groups related route definitions and can be included into
        FastHTTP or other Router instances.

        Args:
            base_url: Base URL used to resolve relative route paths.
            prefix: Shared path prefix for all routes.
            tags: Shared tags inherited by all routes.
            dependencies: Shared dependencies inherited by all routes.
        """
        self.base_url = base_url
        self.prefix = prefix
        self.tags = tags or []
        self.dependencies = dependencies or []
        self._route_defs: list[_RouteDef] = []
        self._include_defs: list[_IncludeDef] = []

    def include_router(
        self,
        router: Annotated[
            Router,
            Doc(
                """
                Child router to include into this router.

                Nested routers allow building larger applications from
                small reusable route groups.
                """
            ),
        ],
        *,
        prefix: Annotated[
            str,
            Doc(
                """
                Optional prefix added before the child router prefix.
                """
            ),
        ] = "",
        tags: Annotated[
            list[str] | None,
            Doc(
                """
                Optional tags prepended before child router tags.
                """
            ),
        ] = None,
        dependencies: Annotated[
            list | None,
            Doc(
                """
                Optional dependencies prepended before child router
                dependencies.
                """
            ),
        ] = None,
        base_url: Annotated[
            str | None,
            Doc(
                """
                Optional base URL override for the child router tree.
                """
            ),
        ] = None,
    ) -> None:
        """
        Include another router into this router.

        Args:
            router: Child router.
            prefix: Additional prefix applied before the child router prefix.
            tags: Tags appended before child route tags.
            dependencies: Dependencies executed before child route dependencies.
            base_url: Optional base_url override for the included router tree.
        """
        self._include_defs.append(
            _IncludeDef(
                router=router,
                prefix=prefix,
                tags=tags or [],
                dependencies=dependencies or [],
                base_url=base_url,
            )
        )

    def _add_route(
        self,
        *,
        method: Literal["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
        url: str,
        params: dict | None = None,
        json: dict | None = None,
        data: object | None = None,
        response_model: type[BaseModel] | None = None,
        request_model: type[BaseModel] | None = None,
        tags: list[str] | None = None,
        dependencies: list | None = None,
        skip_request: bool = False,
        responses: dict[int, dict[Literal["model"], type[BaseModel]]] | None = None,
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
        """
        Register a route definition on the router.

        This stores the route in an unresolved form until `build_routes()`
        is called.
        """
        def decorator(func: Callable[..., object]) -> Callable[..., object]:
            validate_handler(func=func)

            self._route_defs.append(
                _RouteDef(
                    method=method,
                    url=url,
                    handler=func,
                    params=params,
                    json=json,
                    data=data,
                    response_model=response_model,
                    request_model=request_model,
                    tags=tags or [],
                    dependencies=dependencies or [],
                    skip_request=skip_request,
                    responses=responses or {},
                )
            )
            return func

        return decorator

    def get(
        self,
        url: Annotated[
            str,
            Doc(
                """
                Route URL or path.

                Can be an absolute URL like
                `https://api.example.com/users`
                or a relative path like `/users`.
                """
            ),
        ],
        *,
        params: Annotated[
            dict | None,
            Doc("Query parameters for the GET request."),
        ] = None,
        response_model: Annotated[
            type[BaseModel] | None,
            Doc("Optional Pydantic model for validating the handler result."),
        ] = None,
        request_model: Annotated[
            type[BaseModel] | None,
            Doc("Optional Pydantic model for validating request data."),
        ] = None,
        tags: Annotated[
            list[str] | None,
            Doc("Optional tags for grouping and filtering the route."),
        ] = None,
        dependencies: Annotated[
            list | None,
            Doc("Optional dependencies executed before the request."),
        ] = None,
        responses: Annotated[
            dict[int, dict[Literal["model"], type[BaseModel]]] | None,
            Doc("Optional response models for error status codes."),
        ] = None,
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
        """Decorator for registering a GET route on the router."""
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
        url: Annotated[
            str,
            Doc("Route URL or path for the POST request."),
        ],
        *,
        json: Annotated[
            dict | None,
            Doc("Optional JSON body sent with the POST request."),
        ] = None,
        data: Annotated[
            object | None,
            Doc("Optional raw body or form data for the POST request."),
        ] = None,
        response_model: Annotated[
            type[BaseModel] | None,
            Doc("Optional Pydantic model for validating the handler result."),
        ] = None,
        request_model: Annotated[
            type[BaseModel] | None,
            Doc("Optional Pydantic model for validating request data."),
        ] = None,
        tags: Annotated[
            list[str] | None,
            Doc("Optional tags for grouping and filtering the route."),
        ] = None,
        dependencies: Annotated[
            list | None,
            Doc("Optional dependencies executed before the request."),
        ] = None,
        responses: Annotated[
            dict[int, dict[Literal["model"], type[BaseModel]]] | None,
            Doc("Optional response models for error status codes."),
        ] = None,
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
        """Decorator for registering a POST route on the router."""
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
        url: Annotated[
            str,
            Doc("Route URL or path for the PUT request."),
        ],
        *,
        json: Annotated[
            dict | None,
            Doc("Optional JSON body sent with the PUT request."),
        ] = None,
        data: Annotated[
            object | None,
            Doc("Optional raw body or form data for the PUT request."),
        ] = None,
        response_model: Annotated[
            type[BaseModel] | None,
            Doc("Optional Pydantic model for validating the handler result."),
        ] = None,
        request_model: Annotated[
            type[BaseModel] | None,
            Doc("Optional Pydantic model for validating request data."),
        ] = None,
        tags: Annotated[
            list[str] | None,
            Doc("Optional tags for grouping and filtering the route."),
        ] = None,
        dependencies: Annotated[
            list | None,
            Doc("Optional dependencies executed before the request."),
        ] = None,
        responses: Annotated[
            dict[int, dict[Literal["model"], type[BaseModel]]] | None,
            Doc("Optional response models for error status codes."),
        ] = None,
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
        """Decorator for registering a PUT route on the router."""
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
        url: Annotated[
            str,
            Doc("Route URL or path for the PATCH request."),
        ],
        *,
        json: Annotated[
            dict | None,
            Doc("Optional JSON body sent with the PATCH request."),
        ] = None,
        data: Annotated[
            object | None,
            Doc("Optional raw body or form data for the PATCH request."),
        ] = None,
        response_model: Annotated[
            type[BaseModel] | None,
            Doc("Optional Pydantic model for validating the handler result."),
        ] = None,
        request_model: Annotated[
            type[BaseModel] | None,
            Doc("Optional Pydantic model for validating request data."),
        ] = None,
        tags: Annotated[
            list[str] | None,
            Doc("Optional tags for grouping and filtering the route."),
        ] = None,
        dependencies: Annotated[
            list | None,
            Doc("Optional dependencies executed before the request."),
        ] = None,
        responses: Annotated[
            dict[int, dict[Literal["model"], type[BaseModel]]] | None,
            Doc("Optional response models for error status codes."),
        ] = None,
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
        """Decorator for registering a PATCH route on the router."""
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
        url: Annotated[
            str,
            Doc("Route URL or path for the DELETE request."),
        ],
        *,
        json: Annotated[
            dict | None,
            Doc("Optional JSON body sent with the DELETE request."),
        ] = None,
        data: Annotated[
            object | None,
            Doc("Optional raw body or form data for the DELETE request."),
        ] = None,
        response_model: Annotated[
            type[BaseModel] | None,
            Doc("Optional Pydantic model for validating the handler result."),
        ] = None,
        request_model: Annotated[
            type[BaseModel] | None,
            Doc("Optional Pydantic model for validating request data."),
        ] = None,
        tags: Annotated[
            list[str] | None,
            Doc("Optional tags for grouping and filtering the route."),
        ] = None,
        dependencies: Annotated[
            list | None,
            Doc("Optional dependencies executed before the request."),
        ] = None,
        responses: Annotated[
            dict[int, dict[Literal["model"], type[BaseModel]]] | None,
            Doc("Optional response models for error status codes."),
        ] = None,
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
        """Decorator for registering a DELETE route on the router."""
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

    def head(
        self,
        url: Annotated[
            str,
            Doc("Route URL or path for the HEAD request."),
        ],
        *,
        params: Annotated[
            dict | None,
            Doc("Query parameters for the HEAD request."),
        ] = None,
        response_model: Annotated[
            type[BaseModel] | None,
            Doc("Optional Pydantic model for validating the handler result."),
        ] = None,
        request_model: Annotated[
            type[BaseModel] | None,
            Doc("Optional Pydantic model for validating request data."),
        ] = None,
        tags: Annotated[
            list[str] | None,
            Doc("Optional tags for grouping and filtering the route."),
        ] = None,
        dependencies: Annotated[
            list | None,
            Doc("Optional dependencies executed before the request."),
        ] = None,
        responses: Annotated[
            dict[int, dict[Literal["model"], type[BaseModel]]] | None,
            Doc("Optional response models for error status codes."),
        ] = None,
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
        """Decorator for registering a HEAD route on the router."""
        return self._add_route(
            method="HEAD",
            url=url,
            params=params,
            response_model=response_model,
            request_model=request_model,
            tags=tags,
            dependencies=dependencies,
            responses=responses,
        )

    def options(
        self,
        url: Annotated[
            str,
            Doc("Route URL or path for the OPTIONS request."),
        ],
        *,
        params: Annotated[
            dict | None,
            Doc("Query parameters for the OPTIONS request."),
        ] = None,
        response_model: Annotated[
            type[BaseModel] | None,
            Doc("Optional Pydantic model for validating the handler result."),
        ] = None,
        request_model: Annotated[
            type[BaseModel] | None,
            Doc("Optional Pydantic model for validating request data."),
        ] = None,
        tags: Annotated[
            list[str] | None,
            Doc("Optional tags for grouping and filtering the route."),
        ] = None,
        dependencies: Annotated[
            list | None,
            Doc("Optional dependencies executed before the request."),
        ] = None,
        responses: Annotated[
            dict[int, dict[Literal["model"], type[BaseModel]]] | None,
            Doc("Optional response models for error status codes."),
        ] = None,
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
        """Decorator for registering an OPTIONS route on the router."""
        return self._add_route(
            method="OPTIONS",
            url=url,
            params=params,
            response_model=response_model,
            request_model=request_model,
            tags=tags,
            dependencies=dependencies,
            responses=responses,
        )

    def build_routes(
        self,
        *,
        base_url: Annotated[
            str | None,
            Doc("Optional base URL override for this build call."),
        ] = None,
        prefix: Annotated[
            str,
            Doc("Optional prefix added before this router prefix."),
        ] = "",
        tags: Annotated[
            list[str] | None,
            Doc("Optional tags prepended before this router tags."),
        ] = None,
        dependencies: Annotated[
            list | None,
            Doc("Optional dependencies prepended before this router dependencies."),
        ] = None,
    ) -> list[Route]:
        """
        Materialize Router definitions into concrete Route objects.

        Args:
            base_url: Base URL override for this build call.
            prefix: Prefix added before this router prefix.
            tags: Tags prepended before this router tags.
            dependencies: Dependencies prepended before this router dependencies.

        Returns:
            List of resolved Route objects ready for execution.
        """
        merged_base_url = base_url if base_url is not None else self.base_url
        merged_prefix = _join_prefix(prefix, self.prefix)
        merged_tags = (tags or []) + self.tags
        merged_deps = (dependencies or []) + self.dependencies

        routes: list[Route] = []

        for rd in self._route_defs:
            route_tags = merged_tags + rd.tags
            route_deps = merged_deps + rd.dependencies
            resolved_url = _resolve_url(
                url=rd.url,
                base_url=merged_base_url,
                prefix=merged_prefix,
            )
            routes.append(
                Route(
                    method=rd.method,
                    url=resolved_url,
                    handler=rd.handler,
                    params=rd.params,
                    json=rd.json,
                    data=rd.data,
                    response_model=rd.response_model,
                    request_model=rd.request_model,
                    tags=route_tags,
                    dependencies=route_deps,
                    skip_request=rd.skip_request,
                    responses=rd.responses,
                )
            )

        for inc in self._include_defs:
            child_prefix = _join_prefix(merged_prefix, inc.prefix)
            child_tags = merged_tags + inc.tags
            child_deps = merged_deps + inc.dependencies
            child_base_url = (
                inc.base_url
                if inc.base_url is not None
                else merged_base_url
            )
            routes.extend(
                inc.router.build_routes(
                    base_url=child_base_url,
                    prefix=child_prefix,
                    tags=child_tags,
                    dependencies=child_deps,
                )
            )

        return routes

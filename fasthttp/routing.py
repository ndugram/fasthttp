from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .auth import BasicAuth, BearerAuth, DigestAuth, OAuth2ClientCredentials
from .events import ErrorHook, EventHooks, RequestHook, ResponseHook
from .helpers.route_inspect import validate_handler
from .helpers.routing import join_prefix as _join_prefix
from .helpers.routing import resolve_url as _resolve_url
from .types import HTTPMethod  # noqa: TC001

if TYPE_CHECKING:
    from collections.abc import Callable

warnings.filterwarnings(
    "ignore",
    message=r'Field name "json".*shadows',
    category=UserWarning,
    module=r"fasthttp\.routing",
)


class Route(BaseModel):
    """
    Definition of an HTTP request route.

    Binds together an HTTP method, target URL, optional request data,
    and a response handler function.

    Used by FastHTTP to send requests and process responses in a
    structured and predictable way.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    method: HTTPMethod
    """HTTP method for the request (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS)."""

    url: str
    """Target URL for the HTTP request. Must include scheme, host, and path."""

    handler: Any  # Callable[..., object] — kept as Any so Pydantic resolves at runtime
    """Async response handler — called with a Response object."""

    params: dict[str, Any] | None = None
    """Query parameters encoded into the URL query string."""

    json: dict[str, Any] | None = None  # pyright: ignore[reportIncompatibleVariableOverride, reportIncompatibleMethodOverride]
    """JSON body sent with the request (application/json)."""

    data: object | None = None
    """Raw body or form data sent with the request."""

    response_model: type | None = None
    """Optional Pydantic model for validating the handler result."""

    request_model: type[BaseModel] | None = None
    """Optional Pydantic model for validating request data before sending."""

    tags: list[str] = Field(default_factory=list)
    """Tags for grouping and filtering routes."""

    dependencies: list[Any] = Field(default_factory=list)
    """Dependencies executed before the request (e.g. auth, tracing)."""

    skip_request: bool = False
    """When True, skips HTTP execution — handler is responsible for the request."""

    raise_for_status: bool = False
    """When True, raises FastHTTPBadStatusError on 4xx/5xx for this route only."""

    auth: BasicAuth | DigestAuth | BearerAuth | OAuth2ClientCredentials | None = None
    """Authentication for this route (BasicAuth, DigestAuth, BearerAuth, or OAuth2ClientCredentials)."""

    responses: dict[int, dict[Literal["model"], type[BaseModel]]] = Field(
        default_factory=dict
    )
    """Response models for error status codes (e.g. {404: {"model": Error404}})."""

    @field_validator("tags", "dependencies", mode="before")
    @classmethod
    def _coerce_none_to_list(cls, v: list | None) -> list:
        return v if v is not None else []

    @field_validator("responses", mode="before")
    @classmethod
    def _coerce_none_to_dict(cls, v: dict | None) -> dict:
        return v if v is not None else {}

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            method: HTTPMethod,
            url: str,
            handler: Callable[..., object],
            params: dict[str, Any] | None = None,
            json: dict[str, Any] | None = None,
            data: object | None = None,
            response_model: type | None = None,
            request_model: type[BaseModel] | None = None,
            tags: list[str] | None = None,
            dependencies: list[Any] | None = None,
            skip_request: bool = False,
            raise_for_status: bool = False,
            auth: BasicAuth | DigestAuth | BearerAuth | OAuth2ClientCredentials | None = None,
            responses: dict[int, dict[Literal["model"], type[BaseModel]]]
            | None = None,
        ) -> None:
            super().__init__(
                method=method,
                url=url,
                handler=handler,
                params=params,
                json=json,
                data=data,
                response_model=response_model,
                request_model=request_model,
                tags=tags,
                dependencies=dependencies,
                skip_request=skip_request,
                raise_for_status=raise_for_status,
                auth=auth,
                responses=responses,
            )


@dataclass(frozen=True, slots=True)
class _RouteDef:
    """Internal unresolved route definition stored on Router before build_routes()."""

    method: HTTPMethod
    url: str
    handler: Callable[..., object]
    params: dict[str, Any] | None
    json: dict[str, Any] | None
    data: object | None
    response_model: type[BaseModel] | None
    request_model: type[BaseModel] | None
    tags: list[str]
    dependencies: list[Any]
    skip_request: bool
    raise_for_status: bool
    auth: BasicAuth | DigestAuth | BearerAuth | OAuth2ClientCredentials | None
    responses: dict[int, dict[Literal["model"], type[BaseModel]]]


@dataclass(frozen=True, slots=True)
class _IncludeDef:
    """Internal representation of a Router.include_router() call."""

    router: Router
    prefix: str
    tags: list[str]
    dependencies: list[Any]
    base_url: str | None


class Router:
    """
    Router for grouping and composing routes, similar to FastAPI's APIRouter.

    Collects route definitions and can be included into a FastHTTP app
    via ``FastHTTP.include_router(router, ...)``.

    Supports:
    - ``base_url`` (e.g. "https://api.example.com")
    - ``prefix`` (e.g. "/v1")
    - Tags and dependencies inheritance
    - Nested routers via ``include_router()``

    Example:
    ```python
    router = Router(base_url="https://api.example.com", prefix="/v1")

    @router.get("/users")
    async def get_users(resp: Response) -> list:
        return resp.json()
    ```
    """

    def __init__(
        self,
        *,
        base_url: str | None = None,
        prefix: str = "",
        tags: list[str] | None = None,
        dependencies: list[Any] | None = None,
    ) -> None:
        self.base_url = base_url
        self.prefix = prefix
        self.tags: list[str] = tags or []
        self.dependencies: list[Any] = dependencies or []
        self._route_defs: list[_RouteDef] = []
        self._include_defs: list[_IncludeDef] = []
        self.event_hooks = EventHooks()

    def include_router(
        self,
        router: Router,
        *,
        prefix: str = "",
        tags: list[str] | None = None,
        dependencies: list[Any] | None = None,
        base_url: str | None = None,
    ) -> None:
        """Include another router into this router."""
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
        method: HTTPMethod,
        url: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        data: object | None = None,
        response_model: type[BaseModel] | None = None,
        request_model: type[BaseModel] | None = None,
        tags: list[str] | None = None,
        dependencies: list[Any] | None = None,
        skip_request: bool = False,
        raise_for_status: bool = False,
        auth: BasicAuth | DigestAuth | BearerAuth | OAuth2ClientCredentials | None = None,
        responses: dict[int, dict[Literal["model"], type[BaseModel]]] | None = None,
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
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
                    raise_for_status=raise_for_status,
                    auth=auth,
                    responses=responses or {},
                )
            )
            return func

        return decorator

    def get(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        response_model: type[BaseModel] | None = None,
        request_model: type[BaseModel] | None = None,
        tags: list[str] | None = None,
        dependencies: list[Any] | None = None,
        raise_for_status: bool = False,
        auth: BasicAuth | DigestAuth | BearerAuth | OAuth2ClientCredentials | None = None,
        responses: dict[int, dict[Literal["model"], type[BaseModel]]] | None = None,
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
            raise_for_status=raise_for_status,
            auth=auth,
            responses=responses,
        )

    def post(
        self,
        url: str,
        *,
        json: dict[str, Any] | None = None,
        data: object | None = None,
        response_model: type[BaseModel] | None = None,
        request_model: type[BaseModel] | None = None,
        tags: list[str] | None = None,
        dependencies: list[Any] | None = None,
        raise_for_status: bool = False,
        auth: BasicAuth | DigestAuth | BearerAuth | OAuth2ClientCredentials | None = None,
        responses: dict[int, dict[Literal["model"], type[BaseModel]]] | None = None,
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
            raise_for_status=raise_for_status,
            auth=auth,
            responses=responses,
        )

    def put(
        self,
        url: str,
        *,
        json: dict[str, Any] | None = None,
        data: object | None = None,
        response_model: type[BaseModel] | None = None,
        request_model: type[BaseModel] | None = None,
        tags: list[str] | None = None,
        dependencies: list[Any] | None = None,
        raise_for_status: bool = False,
        auth: BasicAuth | DigestAuth | BearerAuth | OAuth2ClientCredentials | None = None,
        responses: dict[int, dict[Literal["model"], type[BaseModel]]] | None = None,
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
            raise_for_status=raise_for_status,
            auth=auth,
            responses=responses,
        )

    def patch(
        self,
        url: str,
        *,
        json: dict[str, Any] | None = None,
        data: object | None = None,
        response_model: type[BaseModel] | None = None,
        request_model: type[BaseModel] | None = None,
        tags: list[str] | None = None,
        dependencies: list[Any] | None = None,
        raise_for_status: bool = False,
        auth: BasicAuth | DigestAuth | BearerAuth | OAuth2ClientCredentials | None = None,
        responses: dict[int, dict[Literal["model"], type[BaseModel]]] | None = None,
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
            raise_for_status=raise_for_status,
            auth=auth,
            responses=responses,
        )

    def delete(
        self,
        url: str,
        *,
        json: dict[str, Any] | None = None,
        data: object | None = None,
        response_model: type[BaseModel] | None = None,
        request_model: type[BaseModel] | None = None,
        tags: list[str] | None = None,
        dependencies: list[Any] | None = None,
        raise_for_status: bool = False,
        auth: BasicAuth | DigestAuth | BearerAuth | OAuth2ClientCredentials | None = None,
        responses: dict[int, dict[Literal["model"], type[BaseModel]]] | None = None,
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
            raise_for_status=raise_for_status,
            auth=auth,
            responses=responses,
        )

    def head(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        response_model: type[BaseModel] | None = None,
        request_model: type[BaseModel] | None = None,
        tags: list[str] | None = None,
        dependencies: list[Any] | None = None,
        raise_for_status: bool = False,
        auth: BasicAuth | DigestAuth | BearerAuth | OAuth2ClientCredentials | None = None,
        responses: dict[int, dict[Literal["model"], type[BaseModel]]] | None = None,
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
            raise_for_status=raise_for_status,
            auth=auth,
            responses=responses,
        )

    def options(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        response_model: type[BaseModel] | None = None,
        request_model: type[BaseModel] | None = None,
        tags: list[str] | None = None,
        dependencies: list[Any] | None = None,
        raise_for_status: bool = False,
        auth: BasicAuth | DigestAuth | BearerAuth | OAuth2ClientCredentials | None = None,
        responses: dict[int, dict[Literal["model"], type[BaseModel]]] | None = None,
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
            raise_for_status=raise_for_status,
            auth=auth,
            responses=responses,
        )

    def on_request(
        self,
        func: RequestHook,
    ) -> RequestHook:
        """
        Register a hook that runs before each request.

        Example:
            ```python
            router = Router(base_url="https://api.example.com")

            @router.on_request
            async def log_request(route: Route, config: dict) -> None:
                print(f"→ {route.method} {route.url}")
            ```
        """
        self.event_hooks.on_request(func)
        return func

    def on_response(
        self,
        func: ResponseHook,
    ) -> ResponseHook:
        """
        Register a hook that runs after each response.

        Example:
            ```python
            @router.on_response
            async def log_response(response: Response) -> None:
                print(f"← {response.status}")
            ```
        """
        self.event_hooks.on_response(func)
        return func

    def on_error(
        self,
        func: ErrorHook,
    ) -> ErrorHook:
        """
        Register a hook that runs when an error occurs.

        Example:
            ```python
            @router.on_error
            async def log_error(error: Exception, route: Route) -> None:
                print(f"✖ {error}")
            ```
        """
        self.event_hooks.on_error(func)
        return func

    def build_routes(
        self,
        *,
        base_url: str | None = None,
        prefix: str = "",
        tags: list[str] | None = None,
        dependencies: list[Any] | None = None,
    ) -> list[Route]:
        """
        Materialize Router definitions into concrete Route objects.

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
                    raise_for_status=rd.raise_for_status,
                    auth=rd.auth,
                    responses=rd.responses,
                )
            )

        for inc in self._include_defs:
            child_prefix = _join_prefix(merged_prefix, inc.prefix)
            child_tags = merged_tags + inc.tags
            child_deps = merged_deps + inc.dependencies
            child_base_url = (
                inc.base_url if inc.base_url is not None else merged_base_url
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

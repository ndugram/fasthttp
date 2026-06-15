from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Annotated, Any

from annotated_doc import Doc

if TYPE_CHECKING:
    from fasthttp.response import Response
    from fasthttp.routing import Route

RequestHook = Callable[..., Coroutine[Any, Any, None]]
ResponseHook = Callable[..., Coroutine[Any, Any, None]]
ErrorHook = Callable[..., Coroutine[Any, Any, None]]


class EventHooks:
    """
    Manages event hooks for request/response lifecycle.

    Provides decorators for registering callbacks that run
    before requests, after responses, and on errors.

    Hook signatures:

    - ``on_request``: ``async def hook(route: Route, config: dict) -> None``
    - ``on_response``: ``async def hook(response: Response) -> None``
    - ``on_error``: ``async def hook(error: Exception, route: Route) -> None``
    """

    def __init__(self) -> None:
        self._on_request: list[RequestHook] = []
        self._on_response: list[ResponseHook] = []
        self._on_error: list[ErrorHook] = []

    def on_request(
        self,
        func: Annotated[
            RequestHook,
            Doc(
                "Async function called before each request. "
                "Signature: async def hook(route: Route, config: dict) -> None"
            ),
        ],
    ) -> RequestHook:
        """
        Register a hook that runs before each request.

        Example:
            ```python
            @app.on_request
            async def log_request(route: Route, config: dict) -> None:
                print(f"→ {route.method} {route.url}")
            ```
        """
        self._on_request.append(func)
        return func

    def on_response(
        self,
        func: Annotated[
            ResponseHook,
            Doc(
                "Async function called after each response. "
                "Signature: async def hook(response: Response) -> None"
            ),
        ],
    ) -> ResponseHook:
        """
        Register a hook that runs after each response.

        Example:
            ```python
            @app.on_response
            async def log_response(response: Response) -> None:
                print(f"← {response.status}")
            ```
        """
        self._on_response.append(func)
        return func

    def on_error(
        self,
        func: Annotated[
            ErrorHook,
            Doc(
                "Async function called on error. "
                "Signature: async def hook(error: Exception, route: Route) -> None"
            ),
        ],
    ) -> ErrorHook:
        """
        Register a hook that runs when an error occurs.

        Example:
            ```python
            @app.on_error
            async def log_error(error: Exception, route: Route) -> None:
                print(f"✖ {error} on {route.url}")
            ```
        """
        self._on_error.append(func)
        return func

    async def process_request(
        self,
        route: Annotated[Route, Doc("The route being executed.")],
        config: Annotated[dict[str, Any], Doc("Request configuration.")],
    ) -> None:
        for hook in self._on_request:
            await hook(route, config)

    async def process_response(
        self,
        response: Annotated[Response, Doc("The HTTP response.")],
    ) -> None:
        for hook in self._on_response:
            await hook(response)

    async def process_error(
        self,
        error: Annotated[Exception, Doc("The exception that occurred.")],
        route: Annotated[Route, Doc("The route that failed.")],
    ) -> None:
        for hook in self._on_error:
            await hook(error, route)

    def merge(self, other: EventHooks) -> None:
        """Merge hooks from another EventHooks instance (used by Router)."""
        self._on_request.extend(other._on_request)
        self._on_response.extend(other._on_response)
        self._on_error.extend(other._on_error)

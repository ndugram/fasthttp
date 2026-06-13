from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any, ClassVar

from annotated_doc import Doc

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

    from fasthttp.response import Response
    from fasthttp.routing import Route
    from fasthttp.types import RequestsOptinal


class BaseMiddleware:
    """
    Base class for middleware in FastHTTP.

    Override :meth:`request` and/or :meth:`response` to intercept requests
    and responses. Override :meth:`on_error` to handle errors.

    Class attributes:

    - ``__return_type__``: expected type this middleware operates on.
    - ``__priority__``: execution order — lower value runs first.
    - ``__methods__``: HTTP methods to apply to (``None`` = all).
    - ``__enabled__``: set to ``False`` to skip without removing from chain.

    Example:
    ```python
        from fasthttp.middleware import BaseMiddleware

        class LoggingMiddleware(BaseMiddleware):
            __priority__ = 0
            __methods__ = ("GET", "POST")  # tuple — immutable default

            async def request(self, method, url, kwargs):
                print(f"→ {method} {url}")
                return kwargs

            async def response(self, response):
                print(f"← {response.status}")
                return response

        app = FastHTTP(middleware=[LoggingMiddleware()])
    ```
    """

    __return_type__: ClassVar[type | None] = None
    __priority__: ClassVar[int] = 0
    __methods__: ClassVar[Sequence[str] | None] = None
    __enabled__: ClassVar[bool] = True

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} return_type={self.__return_type__}>"

    def __or__(self, other: BaseMiddleware) -> MiddlewareChain:
        """Combine two middleware into a :class:`MiddlewareChain` via ``|``."""
        return MiddlewareChain([self, other])

    async def request(
        self,
        method: Annotated[  # noqa: ARG002
            str,
            Doc("HTTP method (GET, POST, etc.)."),
        ],
        url: Annotated[  # noqa: ARG002
            str,
            Doc("Resolved request URL."),
        ],
        kwargs: Annotated[
            dict[str, Any],
            Doc(
                """
                Request keyword arguments (headers, params, json, data, timeout).

                Modifications will be applied to the request before it is sent.
                Always use ``kwargs.get('headers') or {}`` before adding header keys.
                """
            ),
        ],
    ) -> Annotated[
        dict[str, Any],
        Doc("Modified or original kwargs dict passed to the next middleware or httpx."),
    ]:
        """Called before the HTTP request is sent."""
        return kwargs

    async def response(
        self,
        response: Annotated[
            Response,
            Doc("Wrapped Response object."),
        ],
    ) -> Annotated[
        Response,
        Doc("Modified or replaced response passed back up the chain."),
    ]:
        """Called after the HTTP response is received."""
        return response

    async def on_error(
        self,
        error: Annotated[
            Exception,
            Doc("The exception that occurred."),
        ],
        route: Annotated[
            Route,
            Doc("The route that failed."),
        ],
        config: Annotated[
            RequestsOptinal,
            Doc("Request configuration that was used."),
        ],
    ) -> Annotated[
        None,
        Doc("No return value. Called for side effects only."),
    ]:
        """Called when an error occurs during the request."""


class MiddlewareChain:
    """Ordered chain of :class:`BaseMiddleware` instances.

    Created via the ``|`` operator on middleware objects.
    Passed directly to :class:`~fasthttp.app.FastHTTP` as ``middleware=``.

    Example:
    ```python
        chain = AuthMiddleware() | LoggingMiddleware() | TimingMiddleware()
        app = FastHTTP(middleware=chain)
    ```
    """

    def __init__(self, middlewares: list[BaseMiddleware]) -> None:
        self._middlewares = middlewares

    def __or__(self, other: BaseMiddleware) -> MiddlewareChain:
        """Append another middleware to the chain via ``|``."""
        return MiddlewareChain([*self._middlewares, other])

    def __repr__(self) -> str:
        names = ", ".join(m.__class__.__name__ for m in self._middlewares)
        return f"<MiddlewareChain [{names}]>"

    def __iter__(self) -> Iterator[BaseMiddleware]:
        return iter(self._middlewares)

    def __len__(self) -> int:
        return len(self._middlewares)


class MiddlewareManager:
    """
    Manages execution of middleware chain.

    Accepts a list of :class:`BaseMiddleware` instances or a
    :class:`MiddlewareChain`. Middleware is executed in ``__priority__``
    order on requests and in reverse order on responses.
    """

    def __init__(
        self,
        middlewares: Annotated[
            list[BaseMiddleware] | MiddlewareChain | None,
            Doc(
                """
                Middleware to execute. Accepts a list, a MiddlewareChain
                (built via ``|``), or None for no middleware.
                """
            ),
        ] = None,
    ) -> None:
        if isinstance(middlewares, MiddlewareChain):
            self.middlewares: list[BaseMiddleware] = list(middlewares)
        else:
            self.middlewares = middlewares or []

    def _sorted(self) -> list[BaseMiddleware]:
        return sorted(self.middlewares, key=lambda m: m.__priority__)

    def _active(self, middlewares: list[BaseMiddleware], method: str) -> list[BaseMiddleware]:
        result = []
        for mw in middlewares:
            if not mw.__enabled__:
                continue
            if mw.__methods__ is not None and method.upper() not in {
                m.upper() for m in mw.__methods__
            }:
                continue
            result.append(mw)
        return result

    async def process_before_request(
        self,
        route: Annotated[
            Route,
            Doc("The route being executed."),
        ],
        config: Annotated[
            RequestsOptinal,
            Doc("Initial request configuration."),
        ],
    ) -> Annotated[
        dict[str, Any],
        Doc("Final request configuration after middleware processing."),
    ]:
        """Execute all request middleware hooks in priority order."""
        kwargs: dict[str, Any] = dict(config)
        kwargs.setdefault("params", route.params)

        for mw in self._active(self._sorted(), route.method):
            kwargs = await mw.request(route.method, route.url, kwargs)

        return kwargs

    async def process_after_response(
        self,
        response: Annotated[
            Response,
            Doc("The HTTP response object."),
        ],
        route: Annotated[
            Route,
            Doc("The route that was executed."),
        ],
        config: Annotated[  # noqa: ARG002
            RequestsOptinal,
            Doc("Request configuration that was used."),
        ],
    ) -> Annotated[
        Response,
        Doc("Final response after middleware processing."),
    ]:
        """Execute all response middleware hooks in reverse priority order."""
        current = response
        for mw in reversed(self._active(self._sorted(), route.method)):
            current = await mw.response(current)
        return current

    async def process_on_error(
        self,
        error: Annotated[
            Exception,
            Doc("The exception that occurred."),
        ],
        route: Annotated[
            Route,
            Doc("The route that failed."),
        ],
        config: Annotated[
            RequestsOptinal,
            Doc("Request configuration that was used."),
        ],
    ) -> Annotated[
        None,
        Doc("No return value."),
    ]:
        """Execute all on_error middleware hooks in priority order."""
        for mw in self._active(self._sorted(), route.method):
            await mw.on_error(error, route, config)

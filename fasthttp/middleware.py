from __future__ import annotations

import asyncio
import hashlib
import json
import time
from collections import OrderedDict
from contextvars import ContextVar
from typing import TYPE_CHECKING, Annotated, Any, ClassVar

from annotated_doc import Doc

from .types import HTTPMethod

if TYPE_CHECKING:
    from collections.abc import Iterator

    from .response import Response
    from .routing import Route
    from .types import RequestsOptinal


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
            __return_type__ = None
            __priority__ = 0
            __methods__ = None
            __enabled__ = True

            async def request(self, method, url, kwargs):
                print(f"→ {method} {url}")
                return kwargs

            async def response(self, response):
                print(f"← {response.status}")
                return response

        app = FastHTTP(middleware=[LoggingMiddleware()])
    ```
    """

    __return_type__: ClassVar[type | None]
    __priority__: ClassVar[int]
    __methods__: ClassVar[list[HTTPMethod] | None]
    __enabled__: ClassVar[bool]

    def __repr__(self) -> str:
        return_type = getattr(self, "__return_type__", None)
        return f"<{self.__class__.__name__} return_type={return_type}>"

    def __or__(self, other: BaseMiddleware) -> MiddlewareChain:
        """Combine two middleware into a :class:`MiddlewareChain` via ``|``."""
        return MiddlewareChain([self, other])

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)

    async def request(
        self,
        method: Annotated[
            str,
            Doc("HTTP method (GET, POST, etc.)."),
        ],
        url: Annotated[
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
            "Response",
            Doc("Wrapped Response object."),
        ],
    ) -> Annotated[
        "Response",
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
            "Route",
            Doc("The route that failed."),
        ],
        config: Annotated[
            "RequestsOptinal",
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
        return sorted(
            self.middlewares,
            key=lambda m: getattr(m, "__priority__", 0),
        )

    def _active(
        self,
        middlewares: list[BaseMiddleware],
        method: str,
    ) -> list[BaseMiddleware]:
        result = []
        for mw in middlewares:
            if not getattr(mw, "__enabled__", True):
                continue
            allowed = getattr(mw, "__methods__", None)
            if allowed is not None and method.upper() not in {m.upper() for m in allowed}:
                continue
            result.append(mw)
        return result

    async def process_before_request(
        self,
        route: Annotated[
            "Route",
            Doc("The route being executed."),
        ],
        config: Annotated[
            "RequestsOptinal",
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
            "Response",
            Doc("The HTTP response object."),
        ],
        route: Annotated[
            "Route",
            Doc("The route that was executed."),
        ],
        config: Annotated[
            "RequestsOptinal",
            Doc("Request configuration that was used."),
        ],
    ) -> Annotated[
        "Response",
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
            "Route",
            Doc("The route that failed."),
        ],
        config: Annotated[
            "RequestsOptinal",
            Doc("Request configuration that was used."),
        ],
    ) -> Annotated[
        None,
        Doc("No return value."),
    ]:
        """Execute all on_error middleware hooks in priority order."""
        for mw in self._active(self._sorted(), route.method):
            await mw.on_error(error, route, config)


class CacheEntry:
    """Cached response entry with expiration time."""

    def __init__(
        self,
        response: Annotated["Response", Doc("The HTTP response to cache.")],
        ttl: Annotated[int, Doc("Time to live in seconds.")],
    ) -> None:
        self.response = response
        self.expires_at = time.time() + ttl


class CacheMiddleware(BaseMiddleware):
    """
    Middleware for caching HTTP responses in memory.

    Caches responses based on HTTP method and URL with query parameters.
    Subsequent requests within the TTL period return cached responses.

    Example:
        ```python
            from fasthttp import FastHTTP
            from fasthttp.middleware import CacheMiddleware

            app = FastHTTP(
                middleware=[CacheMiddleware(ttl=3600, max_size=100)]
            )

            @app.get(url="https://api.example.com/users")
            async def get_users(resp: Response):
                return resp.json()
        ```
    """

    __return_type__ = None
    __priority__ = 0
    __methods__ = None
    __enabled__ = True

    def __init__(
        self,
        ttl: Annotated[
            int,
            Doc("Time to live for cached responses in seconds. Default 3600."),
        ] = 3600,
        max_size: Annotated[
            int,
            Doc("Maximum number of cached responses. Oldest evicted when full."),
        ] = 100,
        cache_methods: Annotated[
            list[str] | None,
            Doc('HTTP methods to cache. Default ["GET"].'),
        ] = None,
    ) -> None:
        self.ttl = ttl
        self.max_size = max_size
        self.cache_methods = cache_methods or ["GET"]
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = asyncio.Lock()
        self._state: ContextVar[tuple[str | None, Any]] = ContextVar(
            f"cache_state_{id(self)}", default=(None, None)
        )

    def _generate_key(self, method: str, url: str, params: Any) -> str:
        key_data = f"{method}:{url}:{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    async def request(self, method: str, url: str, kwargs: dict[str, Any]) -> dict[str, Any]:
        if method not in self.cache_methods:
            self._state.set((None, None))
            return kwargs

        key = self._generate_key(method, url, kwargs.get("params"))

        async with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if time.time() < entry.expires_at:
                    self._cache.move_to_end(key)
                    self._state.set((key, entry.response))
                    return kwargs
                del self._cache[key]

        self._state.set((key, None))
        return kwargs

    async def response(self, response: "Response") -> "Response":
        key, cached = self._state.get()

        if cached is not None:
            return cached

        if key is not None:
            async with self._lock:
                if len(self._cache) >= self.max_size:
                    self._cache.popitem(last=False)
                self._cache[key] = CacheEntry(response, self.ttl)

        return response

    async def on_error(self, error: Exception, route: "Route", config: "RequestsOptinal") -> None:
        key, _ = self._state.get()
        if key is not None:
            async with self._lock:
                self._cache.pop(key, None)

    def clear(self) -> None:
        """Clear all cached responses."""
        self._cache.clear()

    def get_stats(self) -> dict:
        """Return cache statistics."""
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "ttl": self.ttl,
            "methods": self.cache_methods,
        }

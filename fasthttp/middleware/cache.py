from __future__ import annotations

import asyncio
import hashlib
import time
from collections import OrderedDict
from contextvars import ContextVar
from typing import TYPE_CHECKING, Annotated, Any

import orjson
from annotated_doc import Doc

from .base import BaseMiddleware

try:
    from fasthttp._core import cache_key as _rs_cache_key  # type: ignore

    _HAVE_RUST_CACHE_KEY = True
except ImportError:
    _HAVE_RUST_CACHE_KEY = False

if TYPE_CHECKING:
    from fasthttp.response import Response
    from fasthttp.routing import Route
    from fasthttp.types import RequestsOptional


class CacheEntry:
    """Cached response entry with expiration time."""

    __slots__ = ("expires_at", "response")

    def __init__(
        self,
        response: Annotated[Response, Doc("The HTTP response to cache.")],
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

    def _generate_key(self, method: str, url: str, params: Any) -> str:  # noqa: ANN401
        params_json = orjson.dumps(params or {}, option=orjson.OPT_SORT_KEYS).decode()
        if _HAVE_RUST_CACHE_KEY:
            return _rs_cache_key(method, url, params_json)
        key_data = f"{method}:{url}:{params_json}"
        return hashlib.md5(key_data.encode()).hexdigest()  # noqa: S324

    async def request(
        self, method: str, url: str, kwargs: dict[str, Any]
    ) -> dict[str, Any]:
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
                    kwargs["_fasthttp_cached_response"] = entry.response
                    return kwargs
                del self._cache[key]

        self._state.set((key, None))
        return kwargs

    async def response(self, response: Response) -> Response:
        key, cached = self._state.get()

        if cached is not None:
            return cached

        if key is not None:
            async with self._lock:
                if len(self._cache) >= self.max_size:
                    self._cache.popitem(last=False)
                self._cache[key] = CacheEntry(response, self.ttl)

        return response

    async def on_error(
        self,
        error: Exception,  # noqa: ARG002
        route: Route,  # noqa: ARG002
        config: RequestsOptional,  # noqa: ARG002
    ) -> None:
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

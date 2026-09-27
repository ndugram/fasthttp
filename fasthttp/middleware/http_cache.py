from __future__ import annotations

import asyncio
import contextlib
import time
from collections import OrderedDict
from contextvars import ContextVar
from typing import TYPE_CHECKING, Annotated, Any

from annotated_doc import Doc

from .base import BaseMiddleware
from .cache import generate_cache_key

if TYPE_CHECKING:
    from fasthttp.response import Response
    from fasthttp.routing import Route
    from fasthttp.types import RequestsOptional


def parse_cache_control(header: str | None) -> dict[str, str | None]:
    directives: dict[str, str | None] = {}
    if not header:
        return directives
    for part in header.split(","):
        part = part.strip()
        if not part:
            continue
        key, sep, value = part.partition("=")
        directives[key.strip().lower()] = value.strip().strip('"') if sep else None
    return directives


class HTTPCacheEntry:
    """Cached response with HTTP validators, for conditional revalidation."""

    __slots__ = ("etag", "freshness_seconds", "last_modified", "must_revalidate", "response", "stored_at")

    def __init__(
        self,
        response: Response,
        *,
        etag: str | None,
        last_modified: str | None,
        freshness_seconds: float | None,
        must_revalidate: bool,
    ) -> None:
        self.response = response
        self.etag = etag
        self.last_modified = last_modified
        self.freshness_seconds = freshness_seconds
        self.must_revalidate = must_revalidate
        self.stored_at = time.time()

    @property
    def is_fresh(self) -> bool:
        if self.must_revalidate or self.freshness_seconds is None:
            return False
        return (time.time() - self.stored_at) < self.freshness_seconds

    def touch(self) -> None:
        self.stored_at = time.time()


class HTTPCacheMiddleware(BaseMiddleware):
    """
    Middleware that caches responses using real HTTP caching semantics —
    ``ETag``/``If-None-Match``, ``Last-Modified``/``If-Modified-Since``, and
    ``Cache-Control`` (``max-age``, ``no-cache``, ``no-store``,
    ``must-revalidate``) — instead of a flat TTL.

    A stale cached response with a validator is revalidated with a
    conditional request; a ``304 Not Modified`` reuses the cached body
    without re-downloading it. A response with neither a validator nor a
    usable ``max-age``/``default_ttl`` is not cached at all.

    Example:
        ```python
            from fasthttp import FastHTTP
            from fasthttp.middleware import HTTPCacheMiddleware

            app = FastHTTP(
                middleware=[HTTPCacheMiddleware(max_size=200)]
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
        *,
        default_ttl: Annotated[
            float | None,
            Doc(
                "Freshness lifetime (seconds) to assume when a response has "
                "no Cache-Control: max-age. None means: only cache responses "
                "that carry an explicit max-age, ETag, or Last-Modified."
            ),
        ] = None,
        max_size: Annotated[
            int,
            Doc("Maximum number of cached responses. Oldest evicted when full."),
        ] = 100,
        cache_methods: Annotated[
            list[str] | None,
            Doc('HTTP methods to cache. Default ["GET"].'),
        ] = None,
    ) -> None:
        self.default_ttl = default_ttl
        self.max_size = max_size
        self.cache_methods = cache_methods or ["GET"]
        self._cache: OrderedDict[str, HTTPCacheEntry] = OrderedDict()
        self._lock = asyncio.Lock()
        self._state: ContextVar[tuple[str | None, HTTPCacheEntry | None]] = ContextVar(
            f"http_cache_state_{id(self)}", default=(None, None)
        )

    async def request(self, method: str, url: str, kwargs: dict[str, Any]) -> dict[str, Any]:
        if method not in self.cache_methods:
            self._state.set((None, None))
            return kwargs

        key = generate_cache_key(method, url, kwargs.get("params"))

        async with self._lock:
            entry = self._cache.get(key)

        if entry is None:
            self._state.set((key, None))
            return kwargs

        if entry.is_fresh:
            async with self._lock:
                self._cache.move_to_end(key)
            self._state.set((key, None))
            kwargs["_fasthttp_cached_response"] = entry.response
            return kwargs

        headers = dict(kwargs.get("headers") or {})
        if entry.etag:
            headers["If-None-Match"] = entry.etag
        if entry.last_modified:
            headers["If-Modified-Since"] = entry.last_modified
        kwargs["headers"] = headers
        self._state.set((key, entry))
        return kwargs

    async def response(self, response: Response) -> Response:
        key, stale_entry = self._state.get()
        if key is None:
            return response

        if response.status == 304 and stale_entry is not None:
            stale_entry.touch()
            return stale_entry.response

        cache_control = parse_cache_control(response.headers.get("cache-control"))

        if "no-store" in cache_control:
            async with self._lock:
                self._cache.pop(key, None)
            return response

        etag = response.headers.get("etag")
        last_modified = response.headers.get("last-modified")
        must_revalidate = "no-cache" in cache_control or "must-revalidate" in cache_control

        freshness_seconds = self.default_ttl
        max_age = cache_control.get("max-age")
        if max_age is not None:
            with contextlib.suppress(ValueError):
                freshness_seconds = float(max_age)

        if etag is None and last_modified is None and freshness_seconds is None:
            return response

        entry = HTTPCacheEntry(
            response,
            etag=etag,
            last_modified=last_modified,
            freshness_seconds=freshness_seconds,
            must_revalidate=must_revalidate,
        )
        async with self._lock:
            if key not in self._cache and len(self._cache) >= self.max_size:
                self._cache.popitem(last=False)
            self._cache[key] = entry

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
            "default_ttl": self.default_ttl,
            "methods": self.cache_methods,
        }

from __future__ import annotations

import secrets
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, cast

import httpx

from .client import HTTPClient
from .helpers.routing import apply_base_url
from .logging import setup_logger
from .middleware import (
    BaseMiddleware,
    CookieJar,
    DummyCookieJar,
    MiddlewareChain,
    MiddlewareManager,
    SessionMiddleware,
)
from .routing import Route
from .security import Security

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable, Coroutine

    from .response import Response
    from .types import HTTPMethod


async def _passthrough(resp: Response) -> Response:
    return resp


def _headers_dep(extra: dict[str, str]) -> Callable[..., Coroutine[None, None, dict]]:
    async def dep(_route: Route, config: dict) -> dict:
        config["headers"] = {**config.get("headers", {}), **extra}
        return config

    return dep


def _timeout_dep(timeout: float) -> Callable[..., Coroutine[None, None, dict]]:
    async def dep(_route: Route, config: dict) -> dict:
        config["timeout"] = timeout
        return config

    return dep


class AsyncSession:
    """
    Imperative async HTTP session for fasthttp — like httpx.AsyncClient.

    Reuses all fasthttp internals: middleware, security, logging, cookie jar.
    One httpx.AsyncClient lives for the session lifetime (connection pooling).

    Usage:
    ```python
    import asyncio
    from fasthttp import AsyncSession


    async def main():
        async with AsyncSession(
            base_url="https://jsonplaceholder.typicode.com"
        ) as session:
            resp = await session.get("/todos/1")
            print(resp.json())

            resp = await session.post("/posts", json={"title": "foo", "userId": 1})
            print(resp.status)


    asyncio.run(main())
    ```

    Without context manager:
    ```python
    async def main():
        session = AsyncSession(headers={"Authorization": "Bearer token"})
        await session.open()
        resp = await session.get("https://api.example.com/users")
        await session.close()


    asyncio.run(main())
    ```
    """

    def __init__(
        self,
        *,
        base_url: str | None = None,
        headers: dict[str, str] | None = None,
        timeout: float = 30.0,
        http2: bool = False,
        proxy: str | None = None,
        security: bool = True,
        middleware: list[BaseMiddleware]
        | BaseMiddleware
        | MiddlewareChain
        | None = None,
        cookie_jar: CookieJar | None = None,
        debug: bool = False,
        secret_key: bytes | None = None,
    ) -> None:
        self.base_url = base_url
        self._session_headers = dict(headers or {})
        self.http2_enabled = http2
        self.proxy = proxy
        self.logger = setup_logger(debug=debug)

        if middleware is None:
            normalized: list[BaseMiddleware] | MiddlewareChain = []
        elif isinstance(middleware, (MiddlewareChain, list)):
            normalized = middleware
        else:
            normalized = [middleware]

        self.cookie_jar = cookie_jar
        if cookie_jar is not None and not isinstance(cookie_jar, DummyCookieJar):
            session_mw: BaseMiddleware = SessionMiddleware(jar=cookie_jar)
            if isinstance(normalized, list):
                normalized = cast("list[BaseMiddleware]", [session_mw, *normalized])

        self._middleware_manager = MiddlewareManager(
            cast("list[BaseMiddleware] | MiddlewareChain | None", normalized)
        )

        base_config = {"headers": dict(self._session_headers), "timeout": timeout}
        self._request_configs: dict[str, dict] = {
            method: dict(base_config)
            for method in ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS")
        }

        _secret = secret_key or secrets.token_bytes(32)
        self._security = Security(secret_key=_secret) if security else None

        self._http_client = HTTPClient(
            self._request_configs,
            self.logger,
            self._middleware_manager,
            self._security,
        )

        self._client: httpx.AsyncClient | None = None

    async def open(self) -> None:
        """Open the underlying HTTP connection pool."""
        self._client = httpx.AsyncClient(http2=self.http2_enabled, proxy=self.proxy)

    async def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> AsyncSession:  # noqa: PYI034
        await self.open()
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    def _resolve_url(self, url: str) -> str:
        return apply_base_url(url=url, base_url=self.base_url)

    def _build_route(
        self,
        method: HTTPMethod,
        url: str,
        *,
        params: dict | None = None,
        json: dict | None = None,
        data: object | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> Route:
        deps = []
        if headers:
            deps.append(_headers_dep(headers))
        if timeout is not None:
            deps.append(_timeout_dep(timeout))

        return Route(
            method=method,
            url=self._resolve_url(url),
            handler=_passthrough,
            params=params,
            json=json,
            data=data,
            dependencies=deps,
        )

    def _ensure_open(self) -> httpx.AsyncClient:
        if self._client is None:
            msg = "AsyncSession is not open. Use 'async with AsyncSession()' or call await session.open() first."
            raise RuntimeError(msg)
        return self._client

    async def get(
        self,
        url: str,
        *,
        params: dict | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> Response | None:
        return await self._http_client.send(
            self._ensure_open(),
            self._build_route(
                "GET", url, params=params, headers=headers, timeout=timeout
            ),
        )

    async def post(
        self,
        url: str,
        *,
        json: dict | None = None,
        data: object | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> Response | None:
        return await self._http_client.send(
            self._ensure_open(),
            self._build_route(
                "POST", url, json=json, data=data, headers=headers, timeout=timeout
            ),
        )

    async def put(
        self,
        url: str,
        *,
        json: dict | None = None,
        data: object | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> Response | None:
        return await self._http_client.send(
            self._ensure_open(),
            self._build_route(
                "PUT", url, json=json, data=data, headers=headers, timeout=timeout
            ),
        )

    async def patch(
        self,
        url: str,
        *,
        json: dict | None = None,
        data: object | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> Response | None:
        return await self._http_client.send(
            self._ensure_open(),
            self._build_route(
                "PATCH", url, json=json, data=data, headers=headers, timeout=timeout
            ),
        )

    async def delete(
        self,
        url: str,
        *,
        json: dict | None = None,
        data: object | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> Response | None:
        return await self._http_client.send(
            self._ensure_open(),
            self._build_route(
                "DELETE", url, json=json, data=data, headers=headers, timeout=timeout
            ),
        )

    async def head(
        self,
        url: str,
        *,
        params: dict | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> Response | None:
        return await self._http_client.send(
            self._ensure_open(),
            self._build_route(
                "HEAD", url, params=params, headers=headers, timeout=timeout
            ),
        )

    async def options(
        self,
        url: str,
        *,
        params: dict | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> Response | None:
        return await self._http_client.send(
            self._ensure_open(),
            self._build_route(
                "OPTIONS", url, params=params, headers=headers, timeout=timeout
            ),
        )

    async def request(
        self,
        method: str,
        url: str,
        *,
        params: dict | None = None,
        json: dict | None = None,
        data: object | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> Response | None:
        """Generic method for any HTTP verb."""
        return await self._http_client.send(
            self._ensure_open(),
            self._build_route(
                cast("HTTPMethod", method.upper()),
                url,
                params=params,
                json=json,
                data=data,
                headers=headers,
                timeout=timeout,
            ),
        )

    @asynccontextmanager
    async def stream(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        content: bytes | None = None,
        timeout: float | None = None,
    ) -> AsyncGenerator[httpx.Response, None]:
        """Async context manager for streaming HTTP responses (SSE, chunked, etc.).

        Usage:
        ```python
        async with session.stream("POST", "/stream", content=b"...", headers={...}) as resp:
            async for line in resp.aiter_lines():
                print(line)
        ```
        """
        client = self._ensure_open()
        method_upper = method.upper()

        merged_headers: dict[str, str] = {}
        if method_upper in self._request_configs:
            merged_headers.update(self._request_configs[method_upper].get("headers", {}))
        if headers:
            merged_headers.update(headers)

        _timeout = timeout
        if _timeout is None and method_upper in self._request_configs:
            _timeout = self._request_configs[method_upper].get("timeout", 30.0)

        async with client.stream(
            method_upper,
            self._resolve_url(url),
            headers=merged_headers or None,
            content=content,
            timeout=_timeout,
        ) as resp:
            yield resp

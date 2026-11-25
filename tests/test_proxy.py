import asyncio
from typing import Any

import pytest

from fasthttp.app import FastHTTP
from fasthttp.helpers.proxy import mask_proxy_url
from fasthttp.response import Response


class _FakeProxy:
    """Minimal HTTP proxy that records request lines and answers 200."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.requests: list[str] = []
        self._server: asyncio.AbstractServer | None = None

    @property
    def url(self) -> str:
        assert self._server is not None
        port = self._server.sockets[0].getsockname()[1]
        return f"http://127.0.0.1:{port}"

    async def start(self) -> None:
        self._server = await asyncio.start_server(self._handle, "127.0.0.1", 0)

    async def stop(self) -> None:
        assert self._server is not None
        self._server.close()
        await self._server.wait_closed()

    async def _handle(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        request_line = (await reader.readline()).decode().strip()
        self.requests.append(request_line)
        while (await reader.readline()) not in (b"\r\n", b""):
            pass
        body = self.name.encode()
        writer.write(
            b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n"
            + f"Content-Length: {len(body)}\r\nConnection: close\r\n\r\n".encode()
            + body
        )
        await writer.drain()
        writer.close()


@pytest.mark.parametrize(
    ("proxy", "expected"),
    [
        (
            "http://user:secret@proxy.example.com:8080",
            "http://user:***@proxy.example.com:8080",
        ),
        ("socks5://u:p@127.0.0.1:1080", "socks5://u:***@127.0.0.1:1080"),
        ("http://proxy.example.com:8080", "http://proxy.example.com:8080"),
        ("http://user@proxy.example.com", "http://user@proxy.example.com"),
    ],
)
def test_mask_proxy_url(proxy: str, expected: str) -> None:
    assert mask_proxy_url(proxy) == expected


def test_route_proxy_is_stored_on_route() -> None:
    app = FastHTTP()

    @app.get(url="https://example.com/a", proxy="http://127.0.0.1:9999")
    async def with_proxy(resp: Response) -> None:
        return None

    @app.get(url="https://example.com/b")
    async def without_proxy(resp: Response) -> None:
        return None

    assert app.routes[0].proxy == "http://127.0.0.1:9999"
    assert app.routes[1].proxy is None


async def test_routes_use_their_own_proxy() -> None:
    results: list[Any] = []

    app_proxy = _FakeProxy("app-proxy")
    route_proxy = _FakeProxy("route-proxy")
    await app_proxy.start()
    await route_proxy.start()
    try:
        # security=False: the test hosts are fake names that SSRF checks would block.
        app = FastHTTP(proxy=app_proxy.url, security=False)

        @app.get(url="http://service.test/default")
        async def default_route(resp: Response) -> None:
            results.append(resp.text)

        @app.get(url="http://service.test/custom", proxy=route_proxy.url)
        async def custom_route(resp: Response) -> None:
            results.append(resp.text)

        await app._run()
    finally:
        await app_proxy.stop()
        await route_proxy.stop()

    assert app_proxy.requests == ["GET http://service.test/default HTTP/1.1"]
    assert route_proxy.requests == ["GET http://service.test/custom HTTP/1.1"]
    assert sorted(results) == ["app-proxy", "route-proxy"]

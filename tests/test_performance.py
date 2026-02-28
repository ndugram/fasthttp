"""
Performance benchmarks for fasthttp library.
Compares fasthttp against aiohttp for various HTTP scenarios.
"""

import asyncio
import logging
import aiohttp
from aiohttp import web
import pytest

from fasthttp.client import HTTPClient
from fasthttp.routing import Route
from fasthttp.response import Response


# Local test server
async def hello_handler(request):
    return web.Response(text="Hello, World!")


async def json_handler(request):
    return web.json_response({"message": "Hello", "data": [1, 2, 3]})


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def server():
    app = web.Application()
    app.router.add_get("/", hello_handler)
    app.router.add_get("/json", json_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = runner.make_site(host="127.0.0.1", port=8080)
    await site.start()

    yield "http://127.0.0.1:8080"
    await runner.cleanup()


@pytest.fixture
def fasthttp_client():
    return HTTPClient(
        request_configs={
            "GET": {"headers": {}, "timeout": 30.0},
            "POST": {"headers": {}, "timeout": 30.0},
        },
        logger=logging.getLogger(__name__),
    )


async def handler(response: Response) -> str:
    return response.text


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_single_get_request(server, fasthttp_client):
    """Benchmark single GET request - fasthttp vs aiohttp."""
    url = f"{server}/"

    async with aiohttp.ClientSession() as aiohttp_client:
        # fasthttp
        route = Route(method="GET", url=url, handler=handler)
        await fasthttp_client.send(aiohttp_client, route)

        # aiohttp
        await aiohttp_client.get(url)


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_json_response(server, fasthttp_client):
    """Benchmark JSON response - fasthttp vs aiohttp."""
    url = f"{server}/json"

    async with aiohttp.ClientSession() as aiohttp_client:
        # fasthttp
        route = Route(method="GET", url=url, handler=handler)
        await fasthttp_client.send(aiohttp_client, route)

        # aiohttp
        await aiohttp_client.get(url)


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_sequential_requests(server, fasthttp_client):
    """Benchmark 10 sequential requests - fasthttp vs aiohttp."""
    url = f"{server}/"

    async with aiohttp.ClientSession() as aiohttp_client:
        # fasthttp
        for _ in range(10):
            route = Route(method="GET", url=url, handler=handler)
            await fasthttp_client.send(aiohttp_client, route)

        # aiohttp
        for _ in range(10):
            await aiohttp_client.get(url)


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_client_reuse(server, fasthttp_client):
    """Benchmark with reused client - fasthttp vs aiohttp."""
    url = f"{server}/"

    async with aiohttp.ClientSession() as aiohttp_client:
        for _ in range(10):
            route = Route(method="GET", url=url, handler=handler)
            await fasthttp_client.send(aiohttp_client, route)

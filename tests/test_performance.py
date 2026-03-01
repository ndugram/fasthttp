"""Performance benchmarks for fasthttp core components."""

import json

import pytest

from fasthttp.middleware import BaseMiddleware, MiddlewareManager
from fasthttp.response import Response
from fasthttp.routing import Route


def _make_response(
    status: int = 200,
    text: str = '{"message": "success", "data": [1, 2, 3]}',
) -> Response:
    return Response(
        status=status,
        text=text,
        headers={"Content-Type": "application/json", "X-Request-Id": "abc123"},
        method="GET",
        req_headers={"User-Agent": "fasthttp/0.1.8", "Accept": "application/json"},
        query={"page": "1", "limit": "50"},
        req_json=None,
        req_data=None,
    )


# -- Response benchmarks --


@pytest.mark.benchmark
def test_response_creation() -> None:
    _make_response()


@pytest.mark.benchmark
def test_response_json_parsing() -> None:
    resp = _make_response()
    resp.json()


@pytest.mark.benchmark
def test_response_json_parsing_large_payload() -> None:
    payload = json.dumps(
        {"items": [{"id": i, "name": f"item_{i}"} for i in range(100)]}
    )
    resp = _make_response(text=payload)
    resp.json()


@pytest.mark.benchmark
def test_response_repr() -> None:
    resp = _make_response()
    repr(resp)


@pytest.mark.benchmark
def test_response_property_access() -> None:
    resp = _make_response()
    _ = resp.status
    _ = resp.text
    _ = resp.headers
    _ = resp.method
    _ = resp.req_headers
    _ = resp.query
    _ = resp.path_params


@pytest.mark.benchmark
def test_response_req_text_from_json() -> None:
    resp = Response(
        status=200,
        text="{}",
        headers={},
        method="POST",
        req_json={"key": "value", "nested": {"a": 1}},
    )
    resp.req_text()


# -- Route benchmarks --


async def _noop_handler(resp: Response) -> None:
    pass


@pytest.mark.benchmark
def test_route_creation() -> None:
    Route(
        method="GET",
        url="https://api.example.com/users",
        handler=_noop_handler,
        params={"page": "1"},
    )


@pytest.mark.benchmark
def test_route_creation_with_json() -> None:
    Route(
        method="POST",
        url="https://api.example.com/users",
        handler=_noop_handler,
        json={"name": "test", "email": "test@example.com"},
    )


# -- Middleware benchmarks --


@pytest.mark.benchmark
def test_middleware_manager_creation() -> None:
    MiddlewareManager([BaseMiddleware(), BaseMiddleware(), BaseMiddleware()])


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_middleware_before_request() -> None:
    manager = MiddlewareManager([BaseMiddleware(), BaseMiddleware()])
    route = Route(
        method="GET",
        url="https://api.example.com/data",
        handler=_noop_handler,
    )
    config = {"headers": {"Authorization": "Bearer token"}, "timeout": 30.0}
    await manager.process_before_request(route, config)


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_middleware_after_response() -> None:
    manager = MiddlewareManager([BaseMiddleware(), BaseMiddleware()])
    route = Route(
        method="GET",
        url="https://api.example.com/data",
        handler=_noop_handler,
    )
    resp = _make_response()
    config = {"headers": {}, "timeout": 30.0}
    await manager.process_after_response(resp, route, config)


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_middleware_on_error() -> None:
    manager = MiddlewareManager([BaseMiddleware(), BaseMiddleware()])
    route = Route(
        method="GET",
        url="https://api.example.com/data",
        handler=_noop_handler,
    )
    config = {"headers": {}, "timeout": 30.0}
    error = ConnectionError("test error")
    await manager.process_on_error(error, route, config)

"""Performance benchmarks for fasthttp core components."""

import json

import pytest

from fasthttp.middleware import BaseMiddleware, MiddlewareManager
from fasthttp.response import Response
from fasthttp.routing import Route


def _make_response() -> Response:
    return Response(
        status=200,
        text='{"message": "success", "data": [1, 2, 3]}',
        headers={"Content-Type": "application/json", "X-Request-Id": "abc123"},
        method="GET",
        req_headers={"User-Agent": "fasthttp/0.1.8", "Accept": "application/json"},
        query={"page": "1", "limit": "10"},
        req_json=None,
        req_data=None,
    )


@pytest.mark.benchmark
def test_response_creation() -> None:
    """Benchmark creating a Response object."""
    for _ in range(100):
        _make_response()


@pytest.mark.benchmark
def test_response_json_parsing() -> None:
    """Benchmark parsing JSON from a Response."""
    resp = _make_response()
    for _ in range(100):
        resp.json()


@pytest.mark.benchmark
def test_response_properties_access() -> None:
    """Benchmark accessing Response properties."""
    resp = _make_response()
    for _ in range(100):
        _ = resp.status
        _ = resp.text
        _ = resp.headers
        _ = resp.method
        _ = resp.req_headers
        _ = resp.query
        _ = resp.path_params


@pytest.mark.benchmark
def test_route_creation() -> None:
    """Benchmark creating Route objects."""

    async def handler(resp: Response) -> None:
        pass

    for _ in range(100):
        Route(
            method="GET",
            url="https://api.example.com/data",
            handler=handler,
            params={"key": "value"},
            json=None,
            data=None,
            response_model=None,
        )


@pytest.mark.benchmark
def test_middleware_manager_creation() -> None:
    """Benchmark creating a MiddlewareManager with middlewares."""
    middlewares = [BaseMiddleware() for _ in range(5)]
    for _ in range(100):
        MiddlewareManager(middlewares)


@pytest.mark.benchmark
def test_response_repr() -> None:
    """Benchmark Response string representation."""
    resp = _make_response()
    for _ in range(100):
        repr(resp)


@pytest.mark.benchmark
def test_response_req_text_with_json() -> None:
    """Benchmark Response.req_text() with JSON body."""
    resp = Response(
        status=200,
        text='{"result": "ok"}',
        headers={"Content-Type": "application/json"},
        method="POST",
        req_headers={"Content-Type": "application/json"},
        query=None,
        req_json={"name": "test", "value": 42},
        req_data=None,
    )
    for _ in range(100):
        resp.req_text()


@pytest.mark.benchmark
def test_json_loads_various_payloads() -> None:
    """Benchmark JSON parsing with different payload sizes."""
    small = '{"key": "value"}'
    medium = json.dumps({"items": [{"id": i, "name": f"item_{i}"} for i in range(10)]})
    large = json.dumps(
        {
            "items": [
                {"id": i, "name": f"item_{i}", "tags": ["a", "b"]} for i in range(50)
            ]
        }
    )
    for payload in [small, medium, large]:
        resp = Response(
            status=200,
            text=payload,
            headers={"Content-Type": "application/json"},
        )
        for _ in range(50):
            resp.json()

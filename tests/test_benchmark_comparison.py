"""
Benchmark: v1.2.8 (plain Python) vs v1.3.0 (Pydantic + orjson + Rust).

Run:
    uv run pytest tests/test_benchmark_comparison.py -v -s

Prints a comparison table at the end. No external tools required.
"""

from __future__ import annotations

import json
import re
import timeit
from typing import Any
from urllib.parse import urljoin

import pytest

from fasthttp.response import Response as ResponseV130
from fasthttp.routing import Route as RouteV130

NUMBER = 30_000

_HTML = """
<html><head>
<link rel="stylesheet" href="/static/main.css">
<link rel="stylesheet" href="/static/theme.css">
</head><body>
<script src="/static/app.js"></script>
<script src="/static/vendor.js"></script>
</body></html>
"""

# ---------------------------------------------------------------------------
# Inline v1.2.8 implementations (plain Python, stdlib json, pure-regex assets)
# ---------------------------------------------------------------------------

_CSS_RE_128 = re.compile(
    r'<link[^>]+rel=["\']stylesheet["\'][^>]+href=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
_JS_RE_128 = re.compile(r'<script[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)


def _extract_assets_v128(html: str, base_url: str) -> dict:
    css = [urljoin(base_url, m) for m in _CSS_RE_128.findall(html)]
    js = [urljoin(base_url, m) for m in _JS_RE_128.findall(html)]
    return {"css": css, "js": js}


class ResponseV128:
    def __init__(
        self,
        status: int,
        text: str,
        headers: dict,
        method: str | None = None,
        req_headers: dict | None = None,
        query: dict | None = None,
        req_json: dict | None = None,
        req_data: object | None = None,
    ) -> None:
        self.status = status
        self.text = text
        self.headers = headers
        self._method = method
        self._req_headers = req_headers
        self._query = query
        self._req_json = req_json
        self._req_data = req_data
        self._url: str | None = None
        self._handler_result = None

    @property
    def method(self) -> str | None:
        return self._method

    @property
    def req_headers(self) -> dict | None:
        return self._req_headers

    @property
    def query(self) -> dict | None:
        return self._query

    @property
    def url(self) -> str | None:
        return self._url

    @property
    def path_params(self) -> dict:
        return {}

    def json(self) -> Any:
        return json.loads(self.text)

    def req_json(self) -> dict | None:
        return self._req_json

    def req_text(self) -> str | None:
        if self._req_json is not None:
            return json.dumps(self._req_json)
        if self._req_data is not None:
            return str(self._req_data)
        return None

    def assets(self, *, css: bool = True, js: bool = True) -> dict:
        base_url = self._url or ""
        result = _extract_assets_v128(self.text, base_url)
        if not css:
            result["css"] = []
        if not js:
            result["js"] = []
        return result

    def __repr__(self) -> str:
        return f"<Response [{self.status}]>"


class RouteV128:
    def __init__(
        self,
        *,
        method: str,
        url: str,
        handler: Any,
        params: dict | None = None,
        json: dict | None = None,
        data: object | None = None,
        response_model: type | None = None,
        request_model: type | None = None,
        tags: list | None = None,
        dependencies: list | None = None,
        skip_request: bool = False,
        responses: dict | None = None,
    ) -> None:
        self.method = method
        self.url = url
        self.handler = handler
        self.params = params
        self.json = json
        self.data = data
        self.response_model = response_model
        self.request_model = request_model
        self.tags = tags or []
        self.dependencies = dependencies or []
        self.skip_request = skip_request
        self.responses = responses or {}


# ---------------------------------------------------------------------------
# Benchmark helpers
# ---------------------------------------------------------------------------

_RESULTS: dict[str, tuple[float, float]] = {}  # name -> (v128_µs, v130_µs)


def _bench(name: str, stmt_128: Any, stmt_130: Any) -> None:
    t128 = timeit.timeit(stmt_128, number=NUMBER) / NUMBER * 1e6
    t130 = timeit.timeit(stmt_130, number=NUMBER) / NUMBER * 1e6
    _RESULTS[name] = (t128, t130)


async def _noop(resp: Any) -> None:
    pass


# ---------------------------------------------------------------------------
# Tests (each runs one benchmark pair)
# ---------------------------------------------------------------------------


def test_bench_response_creation() -> None:
    def v128() -> None:
        ResponseV128(
            status=200,
            text='{"ok": true}',
            headers={"Content-Type": "application/json"},
            method="GET",
            req_headers={"Accept": "application/json"},
            query={"page": "1"},
        )

    def v130() -> None:
        ResponseV130(
            status=200,
            text='{"ok": true}',
            headers={"Content-Type": "application/json"},
            method="GET",
            req_headers={"Accept": "application/json"},
            query={"page": "1"},
        )

    _bench("Response() creation", v128, v130)


def test_bench_response_json_small() -> None:
    r128 = ResponseV128(status=200, text='{"message":"ok","data":[1,2,3]}', headers={})
    r130 = ResponseV130(status=200, text='{"message":"ok","data":[1,2,3]}', headers={})
    _bench("Response.json() small", r128.json, r130.json)


def test_bench_response_json_large() -> None:
    payload = json.dumps({"items": [{"id": i, "name": f"item_{i}"} for i in range(100)]})
    r128 = ResponseV128(status=200, text=payload, headers={})
    r130 = ResponseV130(status=200, text=payload, headers={})
    _bench("Response.json() large (100 items)", r128.json, r130.json)


def test_bench_response_property_access() -> None:
    r128 = ResponseV128(
        status=200, text="{}", headers={"X": "1"}, method="GET",
        req_headers={"A": "B"}, query={"q": "1"},
    )
    r130 = ResponseV130(
        status=200, text="{}", headers={"X": "1"}, method="GET",
        req_headers={"A": "B"}, query={"q": "1"},
    )

    def v128() -> None:
        _ = r128.status; _ = r128.text; _ = r128.headers
        _ = r128.method; _ = r128.req_headers; _ = r128.query

    def v130() -> None:
        _ = r130.status; _ = r130.text; _ = r130.headers
        _ = r130.method; _ = r130.req_headers; _ = r130.query

    _bench("Response property access (6 fields)", v128, v130)


def test_bench_route_creation_get() -> None:
    def v128() -> None:
        RouteV128(method="GET", url="https://api.example.com/users", handler=_noop)

    def v130() -> None:
        RouteV130(method="GET", url="https://api.example.com/users", handler=_noop)

    _bench("Route() GET", v128, v130)


def test_bench_route_creation_post() -> None:
    def v128() -> None:
        RouteV128(
            method="POST", url="https://api.example.com/users", handler=_noop,
            json={"name": "test", "email": "test@example.com"},
        )

    def v130() -> None:
        RouteV130(
            method="POST", url="https://api.example.com/users", handler=_noop,
            json={"name": "test", "email": "test@example.com"},
        )

    _bench("Route() POST + json body", v128, v130)


def test_bench_extract_assets_standalone() -> None:
    try:
        from fasthttp._core import extract_assets as _rust_ext
        rust_available = True
    except ImportError:
        rust_available = False

    if not rust_available:
        pytest.skip("Rust _core not available")

    def v128() -> None:
        _extract_assets_v128(_HTML, "https://example.com")

    def v130() -> None:
        _rust_ext(_HTML, "https://example.com")

    _bench("extract_assets() standalone", v128, v130)


def test_bench_assets_via_response() -> None:
    r128 = ResponseV128(status=200, text=_HTML, headers={})
    r130 = ResponseV130(status=200, text=_HTML, headers={})
    _bench("Response.assets() (via Response obj)", r128.assets, r130.assets)


# ---------------------------------------------------------------------------
# Print results after all tests collected
# ---------------------------------------------------------------------------


def test_zz_print_results() -> None:
    """Print comparison table (runs last due to 'zz' prefix)."""
    col = 36
    print()
    print("=" * 72)
    print(f"  {'Benchmark':<{col}} {'v1.2.8':>8}  {'v1.3.0':>8}  {'Δ':>10}")
    print("=" * 72)
    for name, (t128, t130) in _RESULTS.items():
        ratio = t130 / t128
        if ratio < 1:
            delta = f"+{1/ratio:.1f}x faster"
        else:
            delta = f"-{ratio:.1f}x slower"
        print(f"  {name:<{col}} {t128:>7.3f}µs  {t130:>7.3f}µs  {delta:>12}")
    print("=" * 72)
    print(f"  {'All times: µs per operation, n=' + str(NUMBER)}")
    print()

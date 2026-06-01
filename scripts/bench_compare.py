"""
Compare fasthttp-client performance between two versions.

Usage:
    uv run python scripts/bench_compare.py 1.2.8 1.3.0
    uv run python scripts/bench_compare.py 1.2.8 current
"""

from __future__ import annotations

import subprocess
import sys
import textwrap

# ---------------------------------------------------------------------------
# Benchmark code — runs inside each isolated version environment
# ---------------------------------------------------------------------------

_BENCH_CODE = textwrap.dedent("""
import json as _json
import timeit
import sys

try:
    import orjson as _orjson
    _HAS_ORJSON = True
except ImportError:
    _HAS_ORJSON = False

from fasthttp.response import Response
from fasthttp.routing import Route

NUMBER = 30_000

_HTML = '''
<html><head>
<link rel="stylesheet" href="/static/main.css">
<link rel="stylesheet" href="/static/theme.css">
</head><body>
<script src="/static/app.js"></script>
<script src="/static/vendor.js"></script>
</body></html>
'''

async def _handler(resp): pass

kw_resp = dict(
    status=200,
    text='{"message":"ok","data":[1,2,3]}',
    headers={"Content-Type": "application/json"},
    method="GET",
    req_headers={"Accept": "application/json"},
    query={"page": "1"},
)

kw_route_get = dict(method="GET", url="https://api.example.com/users", handler=_handler)
kw_route_post = dict(method="POST", url="https://api.example.com/users", handler=_handler,
                     json={"name": "test", "email": "test@example.com"})

_r = Response(**kw_resp)
_r_big = Response(status=200, headers={},
                  text=_json.dumps({"items": [{"id": i, "name": f"item_{i}"} for i in range(100)]}))
_r_html = Response(status=200, text=_HTML, headers={})

def _t(fn): return timeit.timeit(fn, number=NUMBER) / NUMBER * 1e6

results = {
    "response_creation":          _t(lambda: Response(**kw_resp)),
    "response_json_small":        _t(_r.json),
    "response_json_large":        _t(_r_big.json),
    "response_property_access":   _t(lambda: (
        _r.status, _r.text, _r.headers, _r.method, _r.req_headers, _r.query
    )),
    "route_creation_get":         _t(lambda: Route(**kw_route_get)),
    "route_creation_post":        _t(lambda: Route(**kw_route_post)),
    "response_assets":            _t(_r_html.assets),
}

try:
    from fasthttp._core import extract_assets as _ext
    results["extract_assets_rust"] = _t(lambda: _ext(_HTML, "https://example.com"))
except ImportError:
    import re, urllib.parse
    _CSS = re.compile(r'<link[^>]+rel=["\\'\\']stylesheet["\\'\\'][^>]+href=["\\'\\']([^"\\'\\' ]+)["\\'\\']', re.I)
    _JS  = re.compile(r'<script[^>]+src=["\\'\\']([^"\\'\\' ]+)["\\'\\']', re.I)
    def _py_ext(html, base):
        css = [urllib.parse.urljoin(base, m) for m in _CSS.findall(html)]
        js  = [urllib.parse.urljoin(base, m) for m in _JS.findall(html)]
        return {"css": css, "js": js}
    results["extract_assets_py"] = _t(lambda: _py_ext(_HTML, "https://example.com"))

print("BENCH_START")
for k, v in results.items():
    print(f"{k}={v:.6f}")
print("BENCH_END")
""")

# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

LABELS = {
    "response_creation":        "Response() creation",
    "response_json_small":      "Response.json() small",
    "response_json_large":      "Response.json() large (100 items)",
    "response_property_access": "Response property access (6 fields)",
    "route_creation_get":       "Route() GET",
    "route_creation_post":      "Route() POST + json body",
    "response_assets":          "Response.assets()",
    "extract_assets":           "extract_assets() standalone",
}


def run_bench(version: str, project_root: str) -> dict[str, float]:
    # Strip uv/venv env vars so nested `uv run` picks the right environment
    import os
    clean_env = {
        k: v for k, v in os.environ.items()
        if k not in ("VIRTUAL_ENV", "UV_PROJECT", "UV_PROJECT_ROOT", "UV_RUN_RECURSION_DEPTH")
    }

    if version == "current":
        cmd = ["uv", "run", "--project", project_root, "python", "-c", _BENCH_CODE]
        cwd = project_root
        env = os.environ.copy()
    else:
        cmd = [
            "uv", "run",
            "--with", f"fasthttp-client=={version}",
            "--no-project",
            "python", "-c", _BENCH_CODE,
        ]
        # Run from /tmp so local fasthttp/ dir is NOT on sys.path
        cwd = "/tmp"
        env = clean_env

    print(f"  running fasthttp-client {version}...", flush=True)
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, env=env)

    if result.returncode != 0:
        print(f"\n[ERROR] version {version} failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    data: dict[str, float] = {}
    in_block = False
    for line in result.stdout.splitlines():
        if line == "BENCH_START":
            in_block = True
            continue
        if line == "BENCH_END":
            break
        if in_block and "=" in line:
            k, v = line.split("=", 1)
            key = k.strip()
            # Normalize extract_assets variants → single key so table aligns
            if key in ("extract_assets_rust", "extract_assets_py"):
                key = "extract_assets"
            data[key] = float(v.strip())
    return data


def print_table(v_a: str, v_b: str, a: dict[str, float], b: dict[str, float]) -> None:
    all_keys = list({**a, **b}.keys())

    col = 36
    header = f"  {'Benchmark':<{col}}  {v_a:>9}  {v_b:>9}  {'Δ':>13}  {'Winner':>8}"
    sep = "=" * len(header)

    wins = {v_a: 0, v_b: 0}

    print()
    print(sep)
    print(header)
    print(sep)

    for key in all_keys:
        label = LABELS.get(key, key)
        ta = a.get(key)
        tb = b.get(key)

        if ta is None or tb is None:
            n_a = f"{ta:.3f}µs" if ta is not None else "  n/a  "
            n_b = f"{tb:.3f}µs" if tb is not None else "  n/a  "
            print(f"  {label:<{col}}  {n_a:>9}  {n_b:>9}  {'—':>13}  {'—':>8}")
            continue

        ratio = tb / ta
        if ratio < 1:
            delta = f"+{1/ratio:.1f}x faster"
            winner = v_b
        elif ratio > 1:
            delta = f"-{ratio:.1f}x slower"
            winner = v_a
        else:
            delta = "same"
            winner = "tie"

        if winner in wins:
            wins[winner] += 1

        print(
            f"  {label:<{col}}  {ta:.3f}µs  {tb:.3f}µs  {delta:>13}  {winner:>8}"
        )

    print(sep)
    print()
    print(f"  Score:  {v_a} = {wins[v_a]} wins  |  {v_b} = {wins[v_b]} wins")
    if wins[v_a] > wins[v_b]:
        print(f"\n  🏆  WINNER: {v_a}")
    elif wins[v_b] > wins[v_a]:
        print(f"\n  🏆  WINNER: {v_b}")
    else:
        print("\n  🤝  TIE")
    print()


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: uv run python scripts/bench_compare.py <version_a> <version_b>")
        print("       Use 'current' for the local working version")
        print("  e.g: uv run python scripts/bench_compare.py 1.2.8 1.3.0")
        print("  e.g: uv run python scripts/bench_compare.py 1.2.8 current")
        sys.exit(1)

    v_a, v_b = sys.argv[1], sys.argv[2]

    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print(f"\nBenchmarking fasthttp-client {v_a} vs {v_b} (n=30 000 ops each)\n")

    a = run_bench(v_a, project_root)
    b = run_bench(v_b, project_root)

    print_table(v_a, v_b, a, b)


if __name__ == "__main__":
    main()

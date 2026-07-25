"""
Compare fasthttp-client against requests, aiohttp and httpx.

Spins up a local aiohttp server with a small simulated latency (mimics a
real API instead of a degenerate zero-latency loopback, where async
concurrency wouldn't have anything to overlap and the comparison would be
meaningless), fires N requests at concurrency C through each library's
client, and reports requests/sec (from total batch wall-clock time) plus
per-request latency percentiles.

Run:
    python .github/scripts/lib_benchmark.py
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import statistics
import sys
import time
from pathlib import Path

import aiohttp
import httpx
import requests
from aiohttp import web

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fasthttp import AsyncSession

REQUESTS = 300
CONCURRENCY = 50
WARMUP = 10
SIMULATED_LATENCY = 0.02  # seconds — a typical small-API response time


class BenchResult:
    __slots__ = ("batch_elapsed_s", "sample_latencies_s")

    def __init__(self, batch_elapsed_s: float, sample_latencies_s: list[float]) -> None:
        self.batch_elapsed_s = batch_elapsed_s
        self.sample_latencies_s = sample_latencies_s


async def _handle(_request: web.Request) -> web.Response:
    await asyncio.sleep(SIMULATED_LATENCY)
    return web.json_response({"ok": True})


async def _start_server() -> tuple[web.AppRunner, str]:
    app = web.Application()
    app.router.add_get("/", _handle)
    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]  # type: ignore[union-attr]  # noqa: SLF001
    return runner, f"http://127.0.0.1:{port}/"


async def _bench_fasthttp(url: str) -> BenchResult:
    async with AsyncSession(security=False) as session:
        for _ in range(WARMUP):
            await session.get(url)

        sem = asyncio.Semaphore(CONCURRENCY)
        samples: list[float] = []

        async def one() -> None:
            async with sem:
                start = time.perf_counter()
                await session.get(url)
                samples.append(time.perf_counter() - start)

        batch_start = time.perf_counter()
        await asyncio.gather(*(one() for _ in range(REQUESTS)))
        return BenchResult(time.perf_counter() - batch_start, samples)


async def _bench_httpx(url: str) -> BenchResult:
    async with httpx.AsyncClient() as client:
        for _ in range(WARMUP):
            await client.get(url)

        sem = asyncio.Semaphore(CONCURRENCY)
        samples: list[float] = []

        async def one() -> None:
            async with sem:
                start = time.perf_counter()
                await client.get(url)
                samples.append(time.perf_counter() - start)

        batch_start = time.perf_counter()
        await asyncio.gather(*(one() for _ in range(REQUESTS)))
        return BenchResult(time.perf_counter() - batch_start, samples)


async def _bench_aiohttp(url: str) -> BenchResult:
    async with aiohttp.ClientSession() as session:
        for _ in range(WARMUP):
            async with session.get(url) as resp:
                await resp.read()

        sem = asyncio.Semaphore(CONCURRENCY)
        samples: list[float] = []

        async def one() -> None:
            async with sem:
                start = time.perf_counter()
                async with session.get(url) as resp:
                    await resp.read()
                samples.append(time.perf_counter() - start)

        batch_start = time.perf_counter()
        await asyncio.gather(*(one() for _ in range(REQUESTS)))
        return BenchResult(time.perf_counter() - batch_start, samples)


def _bench_requests(url: str) -> BenchResult:
    with requests.Session() as session:
        for _ in range(WARMUP):
            session.get(url)

        samples: list[float] = []
        batch_start = time.perf_counter()
        for _ in range(REQUESTS):
            start = time.perf_counter()
            session.get(url)
            samples.append(time.perf_counter() - start)
        return BenchResult(time.perf_counter() - batch_start, samples)


def _percentiles(samples_s: list[float]) -> dict[str, float]:
    ms = sorted(v * 1000 for v in samples_s)
    return {
        "median_ms": statistics.median(ms),
        "p95_ms": ms[int(len(ms) * 0.95) - 1],
    }


def _write_json(path: str, payload: dict) -> None:
    Path(path).write_text(json.dumps(payload, indent=2))


def _write_github_output(path: str, rps: dict[str, float]) -> None:
    with Path(path).open("a") as f:
        for name, value in rps.items():
            f.write(f"rps_{name}={value:.0f}\n")


async def main() -> None:
    logging.disable(logging.CRITICAL)  # console logging isn't part of what's being measured

    runner, url = await _start_server()
    try:
        results: dict[str, BenchResult] = {}

        print(f"Benchmarking {REQUESTS} requests @ concurrency {CONCURRENCY} against {url} (+{SIMULATED_LATENCY * 1000:.0f}ms simulated latency)")

        results["fasthttp"] = await _bench_fasthttp(url)
        results["httpx"] = await _bench_httpx(url)
        results["aiohttp"] = await _bench_aiohttp(url)
        results["requests"] = await asyncio.to_thread(_bench_requests, url)
    finally:
        await runner.cleanup()

    rps = {name: REQUESTS / r.batch_elapsed_s for name, r in results.items()}
    latency = {name: _percentiles(r.sample_latencies_s) for name, r in results.items()}

    print("\nrequests/sec & latency:")
    for name in results:
        print(
            f"  {name:<10} {rps[name]:>7.0f} req/s   "
            f"median {latency[name]['median_ms']:>6.1f}ms   p95 {latency[name]['p95_ms']:>6.1f}ms"
        )

    payload = {
        "requests": REQUESTS,
        "concurrency": CONCURRENCY,
        "simulated_latency_ms": SIMULATED_LATENCY * 1000,
        "requests_per_second": rps,
        "latency": latency,
    }
    _write_json("bench_results.json", payload)

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        _write_github_output(github_output, rps)


if __name__ == "__main__":
    asyncio.run(main())

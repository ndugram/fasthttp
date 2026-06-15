import time
from contextvars import ContextVar

from fasthttp import FastHTTP
from fasthttp.response import Response
from fasthttp.routing import Route

start_time: ContextVar[float] = ContextVar("start_time", default=0.0)

app = FastHTTP()


@app.on_request
async def timing_start(route: Route, config: dict) -> None:
    start_time.set(time.perf_counter())


@app.on_response
async def timing_end(response: Response) -> None:
    elapsed = (time.perf_counter() - start_time.get()) * 1000
    print(f"⏱ {elapsed:.2f}ms — {response.status}")


@app.get("https://httpbin.org/delay/1")
async def get_slow(resp: Response) -> dict:
    return resp.json()


@app.get("https://httpbin.org/get")
async def get_fast(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()

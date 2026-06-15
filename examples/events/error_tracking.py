from fasthttp import FastHTTP
from fasthttp.response import Response
from fasthttp.routing import Route

errors: list[dict] = []

app = FastHTTP()


@app.on_error
async def track_error(error: Exception, route: Route) -> None:
    entry = {"url": route.url, "method": route.method, "error": str(error)}
    errors.append(entry)
    print(f"✖ Error: {error}")
    print(f"  Total errors: {len(errors)}")


@app.get("https://httpbin.org/status/500")
async def get_error(resp: Response) -> int:
    return resp.status


@app.get("https://httpbin.org/get")
async def get_ok(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()
    print(f"\nCollected {len(errors)} errors")

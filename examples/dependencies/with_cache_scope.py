from fasthttp import Depends, FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)


async def expensive_operation(_route: object, config: dict) -> dict:
    import uuid

    config.setdefault("headers", {})["X-Request-ID"] = str(uuid.uuid4())
    return config


@app.get(
    url="https://httpbin.org/headers",
    dependencies=[Depends(expensive_operation, use_cache=True, scope="function")],
)
async def with_cache_and_scope(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()

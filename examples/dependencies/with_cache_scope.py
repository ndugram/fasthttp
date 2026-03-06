from fasthttp import FastHTTP, Depends
from fasthttp.response import Response

app = FastHTTP(debug=True)


async def expensive_operation(route, config):
    import uuid
    config.setdefault("headers", {})["X-Request-ID"] = str(uuid.uuid4())
    return config


@app.get(
    url="https://httpbin.org/headers",
    dependencies=[
        Depends(expensive_operation, use_cache=True, scope="function")
        ],
)
async def with_cache_and_scope(resp: Response):
    return resp.json()


if __name__ == "__main__":
    app.run()

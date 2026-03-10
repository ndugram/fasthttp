from fasthttp import FastHTTP, Depends
from fasthttp.response import Response

app = FastHTTP(debug=True)


async def add_bearer_token(route, config):
    config.setdefault("headers", {})["Authorization"] = "Bearer my-secret-token"
    return config


async def add_trace_id(route, config):
    import uuid
    config.setdefault("headers", {})["X-Trace-ID"] = str(uuid.uuid4())
    return config


async def add_custom_header(route, config):
    config.setdefault("headers", {})["X-Custom-Header"] = "CustomValue"
    return config


@app.get(
    url="https://httpbin.org/headers",
    dependencies=[Depends(add_bearer_token), Depends(add_trace_id)],
)
async def with_auth_and_trace(resp: Response) -> dict:
    return resp.json()


@app.get(
    url="https://httpbin.org/headers",
    dependencies=[Depends(add_bearer_token), Depends(add_custom_header)],
)
async def with_custom_header(resp: Response) -> dict:
    return resp.json()


@app.get(
    url="https://httpbin.org/headers",
)
async def without_dependencies(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()

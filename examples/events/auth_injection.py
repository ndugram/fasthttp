from fasthttp import FastHTTP
from fasthttp.response import Response
from fasthttp.routing import Route

app = FastHTTP()


@app.on_request
async def inject_auth(route: Route, config: dict) -> None:
    config["headers"] = config.get("headers") or {}
    config["headers"]["Authorization"] = "Bearer my-secret-token"


@app.get("https://httpbin.org/headers")
async def get_headers(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()

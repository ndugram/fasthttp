from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware
from fasthttp.response import Response
from fasthttp.routing import Route
from fasthttp.types import RequestsOptinal


class LoggingMiddleware(BaseMiddleware):
    async def before_request(
        self, route: Route, config: RequestsOptinal
    ) -> RequestsOptinal:
        print(f"🚀 Sending {route.method} request to {route.url}")
        return config

    async def after_response(
        self, response: Response, route: Route, config: RequestsOptinal
    ) -> Response:
        print(f"✅ Received response with status {response.status}")
        return response


class HeaderMiddleware(BaseMiddleware):
    async def before_request(
        self, route: Route, config: RequestsOptinal
    ) -> RequestsOptinal:
        headers = config.get("headers", {})
        headers["X-Custom-Header"] = "MyCustomValue"
        headers["X-Request-ID"] = "12345"

        config["headers"] = headers
        print("📝 Added custom headers to request")
        return config


app = FastHTTP(middleware=[LoggingMiddleware(), HeaderMiddleware()])


@app.get(url="https://httpbin.org/get")
async def get_data(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()

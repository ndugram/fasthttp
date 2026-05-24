from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware
from fasthttp.response import Response
from fasthttp.routing import Route
from fasthttp.types import RequestsOptinal


class ErrorTrackingMiddleware(BaseMiddleware):
    __return_type__ = None
    __priority__ = 0
    __methods__ = None
    __enabled__ = True

    def __init__(self) -> None:
        self.error_count = 0

    async def on_error(
        self, error: Exception, route: Route, config: RequestsOptinal
    ) -> None:
        self.error_count += 1
        print(f"Error #{self.error_count}: {error.__class__.__name__}")
        print(f"  Route: {route.method} {route.url}")
        print(f"  Message: {error!s}")


class RequestCounterMiddleware(BaseMiddleware):
    __return_type__ = None
    __priority__ = 1
    __methods__ = None
    __enabled__ = True

    def __init__(self) -> None:
        self.success_count = 0

    async def response(self, response: Response) -> Response:
        if response.status < 400:
            self.success_count += 1
            print(f"Successful requests: {self.success_count}")
        return response


app = FastHTTP(middleware=[ErrorTrackingMiddleware(), RequestCounterMiddleware()])


@app.get(url="https://httpbin.org/status/200")
async def success_request(resp: Response) -> str:
    return resp.text


@app.get(url="https://httpbin.org/status/404")
async def not_found_request(resp: Response) -> str:
    return resp.text


@app.get(url="https://httpbin.org/status/500")
async def server_error_request(resp: Response) -> str:
    return resp.text


if __name__ == "__main__":
    app.run()

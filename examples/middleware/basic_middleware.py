from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware
from fasthttp.response import Response


class LoggingMiddleware(BaseMiddleware):
    __return_type__ = None
    __priority__ = 99
    __methods__ = ["GET"]
    __enabled__ = True

    async def request(self, method: str, url: str, kwargs: dict) -> dict:
        print(f"→ {method} {url}")
        return kwargs

    async def response(self, response: Response) -> Response:
        print(f"← {response.status}")
        return response


class HeaderMiddleware(BaseMiddleware):
    __return_type__ = None
    __priority__ = 0
    __methods__ = None
    __enabled__ = True

    async def request(self, method: str, url: str, kwargs: dict) -> dict:
        kwargs["headers"] = kwargs.get("headers") or {}
        kwargs["headers"]["X-Custom-Header"] = "MyCustomValue"
        kwargs["headers"]["X-Request-ID"] = "12345"
        print("Added custom headers to request")
        return kwargs


app = FastHTTP(middleware=[HeaderMiddleware(), LoggingMiddleware()], debug=True)


@app.get(url="https://httpbin.org/get")
async def get_data(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()

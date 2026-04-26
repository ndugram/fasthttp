import json
from contextvars import ContextVar

from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware
from fasthttp.response import Response


class ResponseTransformerMiddleware(BaseMiddleware):
    __return_type__ = None
    __priority__ = 0
    __methods__ = None
    __enabled__ = True

    def __init__(self) -> None:
        self._url: ContextVar[str] = ContextVar("transformer_url", default="")

    async def request(self, method: str, url: str, kwargs: dict) -> dict:
        self._url.set(url)
        return kwargs

    async def response(self, response: Response) -> Response:
        try:
            json_data = response.json()

            if isinstance(json_data, dict):
                json_data["_metadata"] = {
                    "transformed_by": "ResponseTransformerMiddleware",
                    "original_url": self._url.get(),
                    "status_code": response.status,
                }

            response.text = json.dumps(json_data)
            print(f"Transformed response from {self._url.get()}")

        except Exception as e:
            print(f"Could not transform response: {e}")

        return response


app = FastHTTP(middleware=[ResponseTransformerMiddleware()])


@app.get(url="https://httpbin.org/get")
async def get_data(resp: Response) -> dict:
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def get_post(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()

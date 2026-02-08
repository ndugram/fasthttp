import json

from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware
from fasthttp.response import Response
from fasthttp.routing import Route
from fasthttp.types import RequestsOptinal


class ResponseTransformerMiddleware(BaseMiddleware):
    async def after_response(
        self, response: Response, route: Route, config: RequestsOptinal
    ) -> Response:
        try:
            json_data = response.json()

            if isinstance(json_data, dict):
                json_data["_metadata"] = {
                    "transformed_by": "ResponseTransformerMiddleware",
                    "original_url": route.url,
                    "status_code": response.status,
                }

            response.text = json.dumps(json_data)
            print(f"🔄 Transformed response from {route.url}")

        except Exception as e:
            print(f"⚠️  Could not transform response: {e}")

        return response


app = FastHTTP(middleware=[ResponseTransformerMiddleware()])


@app.get(url="https://httpbin.org/get")
async def get_data(resp: Response):
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def get_post(resp: Response):
    return resp.json()


if __name__ == "__main__":
    app.run()

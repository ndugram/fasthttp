from fasthttp import FastHTTP
from fasthttp.response import Response
from fasthttp.routing import Route

app = FastHTTP(debug=True)


@app.on_request
async def log_request(route: Route, config: dict) -> None:
    print(f"→ {route.method} {route.url}")


@app.on_response
async def log_response(response: Response) -> None:
    print(f"← {response.status}")


@app.get("https://httpbin.org/get")
async def get_data(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()

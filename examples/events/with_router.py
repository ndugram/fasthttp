from fasthttp import FastHTTP, Router
from fasthttp.response import Response
from fasthttp.routing import Route

router = Router(base_url="https://httpbin.org")


@router.on_request
async def router_log(route: Route, config: dict) -> None:
    print(f"[router] → {route.method} {route.url}")


@router.on_response
async def router_log_response(response: Response) -> None:
    print(f"[router] ← {response.status}")


@router.get("/get")
async def get_data(resp: Response) -> dict:
    return resp.json()


@router.post("/post")
async def post_data(resp: Response) -> dict:
    return resp.json()


app = FastHTTP(debug=True)


@app.on_request
async def app_log(route: Route, config: dict) -> None:
    print(f"[app] → {route.method} {route.url}")


@app.on_response
async def app_log_response(response: Response) -> None:
    print(f"[app] ← {response.status}")


app.include_router(router)

if __name__ == "__main__":
    app.run()

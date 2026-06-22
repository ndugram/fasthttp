from fasthttp import FastHTTP, Router
from fasthttp.response import Response

router = Router(base_url="https://httpbin.org", prefix="/api")


@router.post(
    url="/upload",
    files={"file": b"Hello from router!"},
)
async def upload(resp: Response) -> dict:
    return resp.json()


app = FastHTTP()
app.include_router(router)


if __name__ == "__main__":
    app.run()

from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.post(
    url="https://httpbin.org/post",
    files={"file": b"Hello, world!"},
)
async def upload_bytes(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()

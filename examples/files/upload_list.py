from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.post(
    url="https://httpbin.org/post",
    files=[
        ("files", ("a.txt", b"content of a", "text/plain")),
        ("files", ("b.txt", b"content of b", "text/plain")),
    ],
)
async def upload_list(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()

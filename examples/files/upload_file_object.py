from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.post(
    url="https://httpbin.org/post",
    files={"file": open(__file__, "rb")},
)
async def upload_open_file(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()

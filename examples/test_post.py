from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.post(url="https://httpbin.org/post")
async def test_post(resp: Response) -> int:
    return resp.status


if __name__ == "__main__":
    app.run()

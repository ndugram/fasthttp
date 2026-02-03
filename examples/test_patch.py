from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.patch(url="https://httpbin.org/patch")
async def test_patch(resp: Response) -> int:
    return resp.status


if __name__ == "__main__":
    app.run()

from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.put(url="https://httpbin.org/put")
async def test_put(resp: Response):
    return resp.status


if __name__ == "__main__":
    app.run()

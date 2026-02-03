from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.delete(url="https://httpbin.org/delete")
async def test_delete(resp: Response) -> int:
    return resp.status


if __name__ == "__main__":
    app.run()

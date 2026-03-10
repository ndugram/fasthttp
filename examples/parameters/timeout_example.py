from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(
    post_request={
        "timeout": 5,
    }
)


@app.get(url="https://httpbin.org/delay/2")
async def delayed_request(resp: Response) -> dict:
    return resp.json()


@app.get(url="https://httpbin.org/delay/10")
async def long_delay(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()

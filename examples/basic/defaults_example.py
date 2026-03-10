from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(
    debug=True,
    get_request={
        "headers": {"User-Agent": "FastHTTP-Client"},
        "timeout": 10,
    },
    post_request={
        "headers": {"Content-Type": "application/json"},
        "timeout": 10,
    },
)


@app.get(url="https://httpbin.org/get")
async def get_request(resp: Response) -> dict:
    return resp.json()


@app.post(url="https://httpbin.org/post", json={"message": "hello"})
async def post_request(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()

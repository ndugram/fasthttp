from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(
    get_request={
        "headers": {
            "Authorization": "Bearer 123",
            "User-Agent": "FastHTTP/0.1",
        },
        "timeout": 5,
    },

)


@app.get(url="https://google.com")
async def profile(resp: Response) -> int:
    return resp.status


if __name__ == "__main__":
    app.run()

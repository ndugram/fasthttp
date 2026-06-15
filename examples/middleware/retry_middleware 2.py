from fasthttp import FastHTTP, RetryMiddleware
from fasthttp.response import Response

app = FastHTTP(
    middleware=RetryMiddleware(
        max_retries=3,
        retry_on={429, 500, 502, 503, 504},
        backoff_factor=0.5,
        max_delay=30.0,
    ),
    debug=True,
)


@app.get("https://httpbin.org/status/500")
async def get_flaky(resp: Response) -> int:
    return resp.status


@app.get("https://httpbin.org/get")
async def get_data(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()

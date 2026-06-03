from fasthttp import FastHTTP
from fasthttp.exceptions import FastHTTPBadStatusError
from fasthttp.response import Response

app = FastHTTP(debug=True, raise_for_status=True)


@app.get(url="https://httpbin.org/status/404")
async def not_found(resp: Response) -> dict:
    return resp.json()


@app.get(url="https://httpbin.org/status/500")
async def server_error(resp: Response) -> dict:
    return resp.json()


@app.get(url="https://httpbin.org/get")
async def success(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    try:
        app.run()
    except FastHTTPBadStatusError as e:
        print(f"Caught error: HTTP {e.status_code} — {e.url}")

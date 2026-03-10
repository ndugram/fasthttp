from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)


@app.get(url="https://httpbin.org/status/500")
async def server_error_test(resp: Response) -> dict:
    print("This won't be printed due to server error")
    return resp.json()


@app.get(url="https://httpbin.org/status/502")
async def bad_gateway_test(resp: Response) -> dict:
    print("This won't be printed due to bad gateway")
    return resp.json()


@app.get(url="https://httpbin.org/status/503")
async def service_unavailable_test(resp: Response) -> dict:
    print("This won't be printed due to service unavailable")
    return resp.json()


if __name__ == "__main__":
    app.run()

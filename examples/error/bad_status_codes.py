from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)


@app.get(url="https://httpbin.org/status/404")
async def not_found_test(resp: Response) -> dict:
    print("This won't be printed due to 404 error")
    return resp.json()


@app.get(url="https://httpbin.org/status/500")
async def server_error_test(resp: Response) -> dict:
    print("This won't be printed due to 500 error")
    return resp.json()


@app.get(url="https://httpbin.org/status/403")
async def forbidden_test(resp: Response) -> dict:
    print("This won't be printed due to 403 error")
    return resp.json()


if __name__ == "__main__":
    app.run()

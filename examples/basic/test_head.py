from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.head(url="https://httpbin.org/get")
async def check_endpoint(resp: Response) -> int:
    print(f"HEAD: {resp.status}")
    print(f"Content-Type: {resp.headers.get('content-type', 'n/a')}")
    print(f"Content-Length: {resp.headers.get('content-length', 'n/a')}")
    return resp.status


if __name__ == "__main__":
    app.run()

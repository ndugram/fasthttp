from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.options(url="https://httpbin.org/get")
async def check_allowed_methods(resp: Response) -> dict:
    allow = resp.headers.get("allow", "")
    print(f"OPTIONS: {resp.status}")
    print(f"Allowed methods: {allow}")
    return {"status": resp.status, "allow": allow}


if __name__ == "__main__":
    app.run()

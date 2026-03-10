from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)


@app.get(url="https://httpbin.org/status/404")
async def error_handling(resp: Response) -> dict:
    if resp.status >= 400:
        return {"error": f"HTTP {resp.status}", "message": "Request failed"}
    return resp.json()


if __name__ == "__main__":
    app.run()

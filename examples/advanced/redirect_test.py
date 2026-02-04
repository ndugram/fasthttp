from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)


@app.get(url="https://httpbin.org/redirect/3")
async def redirect_test(resp: Response):
    return {
        "status": resp.status,
        "history": getattr(resp, "history", [])
    }


if __name__ == "__main__":
    app.run()

from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)


@app.get(url="https://httpbin.org/ip")
async def get_ip(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()

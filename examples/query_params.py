from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)


@app.get(
    url="https://httpbin.org/get",
    params={"page": "1", "limit": "10", "search": "test"}
)
async def query_params(resp: Response):
    return resp.json()


if __name__ == "__main__":
    app.run()

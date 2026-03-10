from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)


@app.post(
    url="https://httpbin.org/post",
    data="plain text data",
)
async def post_with_data(resp: Response) -> str:
    return resp.method


if __name__ == "__main__":
    app.run()

from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)


@app.get(url="https://httpbin.org/get")
async def get_all(resp: Response):
    return resp.json()


@app.post(url="https://httpbin.org/post")
async def post_all(resp: Response):
    return resp.json()


@app.put(url="https://httpbin.org/put")
async def put_all(resp: Response):
    return resp.json()


if __name__ == "__main__":
    app.run()

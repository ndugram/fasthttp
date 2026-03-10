from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)


@app.post(
    url="https://httpbin.org/post", json={"name": "test", "email": "test@example.com"}
)
async def json_post(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()

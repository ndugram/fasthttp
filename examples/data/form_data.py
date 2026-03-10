from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)


@app.post(
    url="https://httpbin.org/post",
    data={"username": "testuser", "password": "testpass"},
)
async def form_data(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()

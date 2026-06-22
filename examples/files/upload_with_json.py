from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.post(
    url="https://httpbin.org/post",
    json={"title": "My photo", "tags": ["nature", "sunset"]},
    files={"file": ("sunset.jpg", b"\xff\xd8\xff\xe0fake-jpeg", "image/jpeg")},
)
async def upload_with_json(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()

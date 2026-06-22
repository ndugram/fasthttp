from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.post(
    url="https://httpbin.org/post",
    files={
        "avatar": ("photo.jpg", b"\xff\xd8\xff\xe0fake-jpeg", "image/jpeg"),
        "document": ("resume.pdf", b"%PDF-1.4 fake-pdf", "application/pdf"),
    },
)
async def upload_multiple(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()

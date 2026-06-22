from pathlib import Path

from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()

FILE = Path(__file__).parent / "sample.txt"


@app.post(
    url="https://httpbin.org/post",
    files={"file": FILE},
)
async def upload_path(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()

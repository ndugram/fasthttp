from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.post(
    url="https://httpbin.org/post",
    files={"file": ("report.csv", b"name,score\nAlice,95\nBob,87\n", "text/csv")},
)
async def upload_with_meta(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()

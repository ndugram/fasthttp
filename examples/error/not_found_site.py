from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)


@app.get(url="https:///niwqGFDQUBCIBciwbecibecc.cloud")
async def test_site(r: Response) -> int:
    return r.status


if __name__ == "__main__":
    app.run()

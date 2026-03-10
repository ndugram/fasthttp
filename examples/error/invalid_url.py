from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)


@app.get(url="invalid://aiohttp.url/")
async def invalid_url_test(resp: Response) -> dict:
    print("This won't be printed due to invalid URL")
    return resp.json()


if __name__ == "__main__":
    app.run()

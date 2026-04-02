from fasthttp import FastHTTP
from fasthttp.response import Response


app = FastHTTP(debug=True)


@app.get(url="https://example.com")
async def get_assets(resp: Response) -> dict:
    return resp.assets()


@app.get(url="https://example.com")
async def get_css_only(resp: Response) -> dict:
    return resp.assets(js=False)


@app.get(url="https://example.com")
async def get_js_only(resp: Response) -> dict:
    return resp.assets(css=False)


if __name__ == "__main__":
    app.run()

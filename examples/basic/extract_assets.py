from fasthttp import FastHTTP
from fasthttp.response import Response


app = FastHTTP(debug=True)


@app.get(url="https://v7-agency.com")
async def get_assets(resp: Response) -> dict:
    return resp.assets()


@app.get(url="https://v7-agency.com")
async def get_css_only(resp: Response) -> dict:
    return resp.assets(js=False)


@app.get(url="https://v7-agency.com")
async def get_js_only(resp: Response) -> dict:
    return resp.assets(css=False)

@app.get(url="https://v7-agency.com")
async def get_js_only_all(resp: Response) -> dict:
    return resp.assets()

app.run()

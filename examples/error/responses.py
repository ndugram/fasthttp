from fasthttp import FastHTTP
from fasthttp.response import Response
from pydantic import BaseModel


class Error404(BaseModel):
    message: str
    documentation_url: str
    status: str


class Error403(BaseModel):
    message: str


app = FastHTTP(debug=True, security=False)


@app.get(
    url="https://api.github.com/gist",
    responses={
        404: {"model": Error404}
    }
)
async def handle_404(resp: Response) -> dict:
    return resp.json()


@app.get(
    url="https://api.github.com/repos",
    responses={
        403: {"model": Error403}
    }
)
async def handle_403(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()

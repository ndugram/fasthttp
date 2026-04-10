from fasthttp import FastHTTP
from fasthttp.response import Response
from pydantic import BaseModel

class TestSwagger(BaseModel):
    origin: str

app = FastHTTP(debug=True)


@app.delete("httpbin.org/delete", response_model=TestSwagger)
async def test_delete(resp: Response) -> int:
    return resp.status




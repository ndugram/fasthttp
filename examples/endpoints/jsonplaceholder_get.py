from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def jsonplaceholder_get(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()

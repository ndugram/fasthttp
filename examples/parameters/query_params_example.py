from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)


@app.get(url="https://jsonplaceholder.typicode.com/posts")
async def get_posts(resp: Response) -> dict:
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/comments", params={"postId": "1"})
async def get_comments(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()

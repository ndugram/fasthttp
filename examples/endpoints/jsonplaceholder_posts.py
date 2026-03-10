from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def get_post(resp: Response) -> dict:
    print(f"Status: {resp.status}")
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/posts")
async def get_all_posts(resp: Response) -> dict:
    return resp.json()


@app.post(
    url="https://jsonplaceholder.typicode.com/posts",
    json={"title": "FastHTTP", "body": "Great library!", "userId": 1},
)
async def create_post(resp: Response) -> dict:
    print(f"Created with status: {resp.status}")
    return resp.json()


if __name__ == "__main__":
    app.run()

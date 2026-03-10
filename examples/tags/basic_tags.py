from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.get(
    url="https://jsonplaceholder.typicode.com/users",
    tags=["users", "v1"]
)
async def get_users(resp: Response) -> dict:
    return resp.json()


@app.get(
    url="https://jsonplaceholder.typicode.com/users/1",
    tags=["users", "v1"],
)
async def get_user_by_id(resp: Response) -> dict:
    return resp.json()


@app.get(
    url="https://jsonplaceholder.typicode.com/posts",
    tags=["posts", "v1"],
)
async def get_posts(resp: Response) -> dict:
    return resp.json()


@app.get(
    url="https://jsonplaceholder.typicode.com/comments",
    tags=["comments", "v2"],
)
async def get_comments(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    print("=== Running all routes ===")
    app.run()

    print("\n=== Running only users ===")
    app.run(tags=["users"])

    print("\n=== Running v1 only ===")
    app.run(tags=["v1"])

    print("\n=== Running users and posts ===")
    app.run(tags=["users", "posts"])

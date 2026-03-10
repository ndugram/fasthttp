from pydantic import BaseModel, Field

from fasthttp import FastHTTP
from fasthttp.response import Response


class Post(BaseModel):
    userId: int
    id: int | None = None
    title: str = Field(..., min_length=1, max_length=100)
    body: str = Field(..., min_length=1)


app = FastHTTP(debug=True)


@app.get(url="https://jsonplaceholder.typicode.com/posts", response_model=list[Post])
async def get_all_posts(resp: Response) -> list[Post]:
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1", response_model=Post)
async def get_post(resp) -> Post:
    return resp.json()


@app.post(
    url="https://jsonplaceholder.typicode.com/posts",
    json={"title": "New Post", "body": "Post body", "userId": 1},
    response_model=Post,
)
async def create_post(resp) -> Post:
    return resp.json()


@app.put(
    url="https://jsonplaceholder.typicode.com/posts/1",
    json={"title": "Updated Post", "body": "Updated body", "userId": 1},
    response_model=Post,
)
async def update_post(resp) -> Post:
    return resp.json()


@app.patch(
    url="https://jsonplaceholder.typicode.com/posts/1",
    json={"title": "Patched Title"},
    response_model=Post,
)
async def patch_post(resp) -> Post:
    return resp.json()


@app.delete(
    url="https://jsonplaceholder.typicode.com/posts/1",
)
async def delete_post(resp) -> None:
    return None


if __name__ == "__main__":
    app.run()

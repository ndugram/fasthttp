from pydantic import BaseModel, Field

from fasthttp import FastHTTP
from fasthttp.response import Response


class Post(BaseModel):
    id: int = Field(description="Post ID")
    title: str = Field(description="Post title")
    body: str = Field(description="Post body")
    userId: int = Field(description="Author user ID")


app = FastHTTP(
    title="Blog API",
    version="2.0.0",
    description="""
## Blog API

Read and create blog posts via [JSONPlaceholder](https://jsonplaceholder.typicode.com).

### Endpoints

- **GET /posts/1** — fetch single post
- **POST /posts** — create post
""",
)


@app.get(
    url="https://jsonplaceholder.typicode.com/posts/1",
    response_model=Post,
    tags=["posts"],
)
async def get_post(resp: Response) -> Post:
    """Get post by ID."""
    return Post(**resp.json())


@app.post(
    url="https://jsonplaceholder.typicode.com/posts",
    json={"title": "Hello", "body": "World", "userId": 1},
    response_model=Post,
    tags=["posts"],
)
async def create_post(resp: Response) -> Post:
    """Create a new post."""
    return Post(**resp.json())


if __name__ == "__main__":
    app.web_run(port=8000)

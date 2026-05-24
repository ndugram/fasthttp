"""
Create and validate example.

This example demonstrates creating data via POST requests
and validating the response with Pydantic models.
"""

from pydantic import BaseModel

from fasthttp import FastHTTP
from fasthttp.response import Response


class PostCreate(BaseModel):
    title: str
    body: str
    userId: int


class PostResponse(BaseModel):
    id: int
    title: str | None = None
    body: str | None = None
    userId: int | None = None


app = FastHTTP()


@app.post(
    url="https://jsonplaceholder.typicode.com/posts",
    json={"title": "Test Post", "body": "Test Body", "userId": 1},
    response_model=PostResponse,
)
async def create_post(resp: Response) -> PostResponse:
    return resp.json()


@app.post(url="https://jsonplaceholder.typicode.com/posts", response_model=PostResponse)
async def create_post_dynamic(resp: Response) -> PostResponse:
    return resp.json()


if __name__ == "__main__":
    app.run()

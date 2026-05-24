from pydantic import BaseModel, Field, field_validator

from fasthttp import FastHTTP
from fasthttp.response import Response


class Post(BaseModel):
    userId: int = Field(..., gt=0, description="User ID must be positive")
    id: int = Field(..., gt=0, description="Post ID must be positive")
    title: str = Field(..., min_length=1, max_length=200, description="Post title")
    body: str = Field(
        ..., min_length=10, description="Post body must be at least 10 characters"
    )

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            msg = "Title cannot be empty"
            raise ValueError(msg)
        return v.strip()


class Todo(BaseModel):
    userId: int = Field(..., gt=0)
    id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1)
    completed: bool


app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1", response_model=Post)
async def get_validated_post(resp: Response) -> Post:
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/todos/1", response_model=Todo)
async def get_todo(resp: Response) -> Todo:
    return resp.json()


if __name__ == "__main__":
    app.run()

"""
Demonstrates OpenAPI schema generation built entirely on Pydantic:
enums, nested models, Field descriptions/examples, and error models
are all picked up automatically via `model_json_schema()` — nothing
is hand-mapped.

Run it, then open:
- http://127.0.0.1:8010/docs    (Swagger UI — filter box, dark mode toggle,
                                  persisted auth, request snippets)
- http://127.0.0.1:8010/redoc   (ReDoc — cleaner read-only view)
- http://127.0.0.1:8010/openapi.json
"""

from enum import Enum

from pydantic import BaseModel, Field

from fasthttp import FastHTTP
from fasthttp.response import Response


class Role(str, Enum):
    """Enum fields resolve to a shared `$ref` + `enum` list, not a plain string."""

    admin = "admin"
    editor = "editor"
    viewer = "viewer"


class Address(BaseModel):
    """Nested models are discovered automatically and added to components/schemas."""

    city: str = Field(description="City name", examples=["Berlin"])
    zip_code: str = Field(description="Postal code", examples=["10115"])


class CreateUserRequest(BaseModel):
    name: str = Field(description="Full name", examples=["Ada Lovelace"])
    role: Role = Role.viewer
    address: Address


class UserResponse(BaseModel):
    id: int
    name: str
    role: Role
    address: Address


class ErrorResponse(BaseModel):
    detail: str = Field(description="Human-readable error message")


app = FastHTTP(
    title="Pydantic-native OpenAPI demo",
    version="1.0.0",
)


@app.post(
    url="https://jsonplaceholder.typicode.com/users",
    request_model=CreateUserRequest,
    response_model=UserResponse,
    responses={404: {"model": ErrorResponse}},
    tags=["users"],
)
async def create_user(resp: Response) -> UserResponse:
    """Create a user (nested model + enum in both request and response)."""
    return resp.json()


@app.get(
    url="https://jsonplaceholder.typicode.com/users",
    response_model=list[UserResponse],
    params={"_limit": 5},
    tags=["users"],
)
async def list_users(resp: Response) -> list[UserResponse]:
    """List users — `_limit` query param is pre-filled as an example in Swagger UI."""
    return resp.json()


if __name__ == "__main__":
    app.web_run(port=8010)

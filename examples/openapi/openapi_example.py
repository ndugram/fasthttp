from fasthttp import FastHTTP
from fasthttp.response import Response
from pydantic import BaseModel, Field


# Define Pydantic models
class UserModel(BaseModel):
    """User response model."""
    id: int = Field(description="User ID")
    name: str = Field(description="User name")
    email: str = Field(description="User email")


class ErrorModel(BaseModel):
    """Error response model."""
    error: str = Field(description="Error message")
    code: int = Field(description="Error code")


# Create FastHTTP app
app = FastHTTP(debug=True)


@app.get(
    url="https://jsonplaceholder.typicode.com/users/1",
    response_model=UserModel,
    tags=["users"],
)
async def get_user(resp: Response) -> dict:
    """Get user by ID."""
    return resp.json()


@app.get(
    url="https://jsonplaceholder.typicode.com/users",
    response_model=list[UserModel],
    tags=["users"],
)
async def get_all_users(resp: Response) -> list[dict]:
    """Get all users."""
    return resp.json()


@app.post(
    url="https://jsonplaceholder.typicode.com/users",
    response_model=UserModel,
    tags=["users"],
)
async def create_user(resp: Response) -> dict:
    """Create a new user."""
    return resp.json()


@app.get(
    url="https://httpbin.org/get",
    tags=["test"],
)
async def test_get(resp: Response) -> dict:
    """Test GET request with params."""
    return resp.json()


@app.post(
    url="https://httpbin.org/post",
    json={"test": "data"},
    tags=["test"],
)
async def test_post(resp: Response) -> dict:
    """Test POST request with JSON body."""
    return resp.json()


if __name__ == "__main__":
    app.web_run(port=9009)

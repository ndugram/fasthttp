# Error Validation

Validate API error responses using Pydantic models.

## Using responses Parameter

The `responses` parameter allows defining Pydantic models for different HTTP status codes.

## Basic Example

```python
from fasthttp import FastHTTP
from fasthttp.response import Response
from pydantic import BaseModel

app = FastHTTP(debug=True, security=False)


class Error404(BaseModel):
    message: str
    documentation_url: str
    status: str


@app.get(
    url="https://api.github.com/gist",
    responses={404: {"model": Error404}}
)
async def handle_404(resp: Response) -> dict:
    return resp.json()


app.run()
```

When server returns an error:
1. FastHTTP looks for model for this status
2. If found, validates JSON response
3. Validated data available via resp.json()

## Multiple Status Codes

```python
class Error404(BaseModel):
    message: str


class Error500(BaseModel):
    error: str
    details: str


@app.get(
    url="https://api.example.com/data",
    responses={
        404: {"model": Error404},
        500: {"model": Error500}
    }
)
async def handle_errors(resp: Response) -> dict:
    return resp.json()
```

## Success and Error Responses

```python
class SuccessResponse(BaseModel):
    id: int
    name: str


class Error404(BaseModel):
    message: str


@app.get(
    url="https://api.example.com/users/1",
    response_model=SuccessResponse,
    responses={404: {"model": Error404}}
)
async def get_user(resp: Response) -> dict:
    return resp.json()
```

## Different HTTP Methods

```python
class Error403(BaseModel):
    message: str


# POST with error handling
@app.post(
    url="https://api.example.com/users",
    json={"name": "John"},
    responses={403: {"model": Error403}}
)
async def create_user(resp: Response) -> dict:
    return resp.json()


# DELETE with error handling
@app.delete(
    url="https://api.example.com/users/1",
    responses={
        403: {"model": Error403},
        404: {"model": Error403}
    }
)
async def delete_user(resp: Response) -> dict:
    return resp.json()
```

## Important Notes

- `responses` works only for APIs returning JSON with errors
- If API returns error without JSON, standard error handling triggers
- Model must match API response structure
- Dictionary key is always integer (HTTP status code)

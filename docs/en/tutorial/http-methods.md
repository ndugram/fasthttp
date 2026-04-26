# HTTP Methods

FastHTTP supports all main HTTP methods.

## GET - Retrieve Data

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.get(url="https://api.example.com/users")
async def get_users(resp: Response) -> dict:
    return resp.json()
```

## POST - Create Data

```python
@app.post(
    url="https://api.example.com/users",
    json={"name": "John", "email": "john@example.com"}
)
async def create_user(resp: Response) -> dict:
    return resp.json()
```

## PUT - Full Update

```python
@app.put(
    url="https://api.example.com/users/1",
    json={"name": "Jane", "email": "jane@example.com"}
)
async def update_user(resp: Response) -> dict:
    return resp.json()
```

## PATCH - Partial Update

```python
@app.patch(
    url="https://api.example.com/users/1",
    json={"age": 25}
)
async def patch_user(resp: Response) -> dict:
    return resp.json()
```

## DELETE - Remove Data

```python
@app.delete(url="https://api.example.com/users/1")
async def delete_user(resp: Response) -> dict:
    return resp.status
```

## HEAD - Check Endpoint

Returns only headers, no body. Useful for checking if a resource exists or inspecting metadata.

```python
@app.head(url="https://api.example.com/users")
async def check_users(resp: Response) -> int:
    return resp.status
```

## OPTIONS - Allowed Methods

Returns the HTTP methods supported by the endpoint.

```python
@app.options(url="https://api.example.com/users")
async def allowed_methods(resp: Response) -> dict:
    return {"allow": resp.headers.get("allow", "")}
```

## Decorator Parameters

| Parameter | Description |
|-----------|-------------|
| `url` | Request URL (required) |
| `params` | Query parameters |
| `json` | JSON body (for POST, PUT, PATCH) |
| `data` | Raw bytes body |
| `tags` | Tags for grouping |
| `dependencies` | List of dependencies |
| `response_model` | Pydantic model for validation |
| `request_model` | Pydantic model for request validation |
| `responses` | Pydantic models for error responses |

## Return Values

Handlers can return different types:

```python
# Return dict - converted to JSON
async def return_dict(resp: Response) -> dict:
    return {"message": "Hello"}

# Return list
async def return_list(resp: Response) -> list:
    return [1, 2, 3]

# Return string
async def return_string(resp: Response) -> str:
    return "Hello, World!"

# Return number (status code)
async def return_number(resp: Response) -> int:
    return resp.status

# Return Response object
async def return_response(resp: Response) -> Response:
    return resp
```

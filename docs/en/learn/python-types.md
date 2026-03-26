# Python Type Annotations

FastHTTP uses Python type annotations extensively. This document explains the type hints used throughout the framework.

## Why Type Annotations?

FastHTTP requires all handler functions to have explicit type annotations:

1. **Parameter annotations** - Each parameter must have a type
2. **Return type annotation** - Function must return a specific type

This is a core requirement of the framework, not optional.

## Basic Usage

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.get(url="https://api.example.com/data")
async def get_data(resp: Response) -> dict:
    """Handler with proper type annotations."""
    return resp.json()
```

## Type Annotations Explained

### Parameter Types

The `Response` object is passed to every handler:

```python
async def handler(resp: Response) -> dict:
    # resp has type Response
```

### Return Types

FastHTTP supports multiple return types:

| Return Type | Description |
|-------------|-------------|
| `dict` | Automatically converted to JSON |
| `list` | Automatically converted to JSON |
| `str` | Returned as text |
| `int` | Returned as number (often status code) |
| `Response` | Return the entire response object |
| `None` | No data to return |

## Common Errors

### Missing Parameter Annotation

```python
# Error - missing type annotation for resp
@app.get(url="https://api.example.com/data")
async def get_data(resp) -> dict:
    return resp.json()

# Fix
async def get_data(resp: Response) -> dict:
    return resp.json()
```

### Missing Return Type Annotation

```python
# Error - missing return type annotation
@app.get(url="https://api.example.com/data")
async def get_data(resp: Response):
    return resp.json()

# Fix
async def get_data(resp: Response) -> dict:
    return resp.json()
```

## Pydantic Models

When using Pydantic for validation, you specify the model as the return type:

```python
from pydantic import BaseModel
from fasthttp import FastHTTP
from fasthttp.response import Response


class User(BaseModel):
    id: int
    name: str
    email: str


app = FastHTTP()


@app.get(
    url="https://api.example.com/users/1",
    response_model=User
)
async def get_user(resp: Response) -> User:
    return resp.json()
```

## Generic Types

FastHTTP supports generic types for lists:

```python
from typing import List
from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str


app = FastHTTP()


@app.get(
    url="https://api.example.com/users",
    response_model=List[User]
)
async def get_users(resp: Response) -> List[User]:
    return resp.json()
```

## Optional Types

Use `Optional` for fields that may be null:

```python
from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    email: Optional[str] = None

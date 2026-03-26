# Pydantic Validation

Validate API responses using Pydantic models.

## Basic Response Validation

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
    url="https://jsonplaceholder.typicode.com/users/1",
    response_model=User
)
async def get_user(resp: Response) -> User:
    return resp.json()
```

FastHTTP automatically validates the response against the Pydantic model.

## Nested Models

```python
from pydantic import BaseModel
from fasthttp import FastHTTP
from fasthttp.response import Response


class Address(BaseModel):
    street: str
    city: str
    zipcode: str


class User(BaseModel):
    id: int
    name: str
    email: str
    address: Address


app = FastHTTP()


@app.get(
    url="https://jsonplaceholder.typicode.com/users/1",
    response_model=User
)
async def get_user(resp: Response) -> User:
    return resp.json()
```

## Lists of Objects

```python
from pydantic import BaseModel
from typing import List
from fasthttp import FastHTTP
from fasthttp.response import Response


class Post(BaseModel):
    userId: int
    id: int
    title: str
    body: str


app = FastHTTP()


@app.get(
    url="https://jsonplaceholder.typicode.com/posts",
    response_model=List[Post]
)
async def get_posts(resp: Response) -> List[Post]:
    return resp.json()
```

## Optional Fields

```python
from pydantic import BaseModel
from typing import Optional
from fasthttp import FastHTTP
from fasthttp.response import Response


class User(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None


app = FastHTTP()


@app.get(
    url="https://jsonplaceholder.typicode.com/users/1",
    response_model=User
)
async def get_user(resp: Response) -> User:
    return resp.json()
```

## Type Conversion

Pydantic automatically converts types:

```python
class User(BaseModel):
    id: int  # String "1" becomes int
    name: str
    is_active: bool  # "true" becomes True
```

## Custom Validators

```python
from pydantic import BaseModel, field_validator


class User(BaseModel):
    name: str
    email: str
    
    @field_validator('email')
    @classmethod
    def email_lowercase(cls, v):
        return v.lower()
```

## Error Handling

```python
from pydantic import BaseModel, ValidationError
from fasthttp import FastHTTP
from fasthttp.response import Response


class User(BaseModel):
    id: int
    name: str


app = FastHTTP()


@app.get(
    url="https://api.example.com/user",
    response_model=User
)
async def get_user(resp: Response):
    try:
        return resp.json()
    except ValidationError as e:
        print(f"Validation error: {e}")
        return {"error": "Invalid response format"}
```

## Supported Types

- Primitives: `str`, `int`, `float`, `bool`
- Collections: `List`, `Dict`, `Set`
- Optional: `Optional[str]`
- Union: `Union[str, int]`
- Datetime: `datetime`, `date`

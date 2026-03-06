# Pydantic Validation

FastHTTP supports response validation using Pydantic.

## Basic Validation

Define a Pydantic model and specify it in the request:

```python
from pydantic import BaseModel
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


class User(BaseModel):
    id: int
    name: str
    email: str


@app.get(
    url="https://jsonplaceholder.typicode.com/users/1",
    response_model=User
)
async def get_user(resp: Response) -> User:
    return resp.json()
```

FastHTTP automatically:
1. Gets JSON response
2. Validates via Pydantic
3. Returns valid object

## Nested Models

```python
from pydantic import BaseModel
from typing import List, Optional
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


class Address(BaseModel):
    street: str
    city: str
    zipcode: str


class User(BaseModel):
    id: int
    name: str
    email: str
    address: Address


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

app = FastHTTP()


class Post(BaseModel):
    userId: int
    id: int
    title: str
    body: str


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

app = FastHTTP()


class User(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None


@app.get(
    url="https://jsonplaceholder.typicode.com/users/1",
    response_model=User
)
async def get_user(resp: Response) -> User:
    return resp.json()
```

## Validation with Conversion

Pydantic automatically converts types:

```python
from pydantic import BaseModel
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


class User(BaseModel):
    id: int  # String "1" will automatically become int
    name: str
    is_active: bool  # "true" -> True


@app.get(
    url="https://api.example.com/users/1",
    response_model=User
)
async def get_user(resp: Response) -> User:
    # Response: {"id": "1", "name": "John", "is_active": "true"}
    # Converts to: User(id=1, name="John", is_active=True)
    return resp.json()
```

## Custom Validators

```python
from pydantic import BaseModel, validator
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


class User(BaseModel):
    name: str
    email: str
    
    @validator('email')
    def email_must_contain_at(cls, v):
        if '@' not in v:
            raise ValueError('Email must contain @')
        return v.lower()  # Automatically to lowercase


@app.get(
    url="https://api.example.com/user",
    response_model=User
)
async def get_user(resp: Response) -> User:
    return resp.json()
```

## Validation Error Handling

```python
from pydantic import BaseModel, ValidationError
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


class User(BaseModel):
    id: int
    name: str


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

## Pydantic Data Types

FastHTTP supports all Pydantic types:

```python
from pydantic import BaseModel
from typing import List, Dict, Optional, Union
from datetime import datetime, date
from fasthttp import FastHTTP

app = FastHTTP()


class CompleteExample(BaseModel):
    # Primitives
    name: str
    age: int
    is_active: bool
    balance: float
    
    # Collections
    tags: List[str]
    metadata: Dict[str, str]
    
    # Optional
    email: Optional[str] = None
    
    # Complex types
    created_at: datetime
    birth_date: date
    
    # Union
    status: Union[str, int]


@app.get(url="https://api.example.com/data", response_model=CompleteExample)
async def handler(resp):
    return resp.json()
```

## See Also

- [Quick Start](quick-start.md) — basics
- [Configuration](configuration.md) — settings
- [Pydantic Docs](https://pydantic-docs.helpmanual.io/) — Pydantic documentation

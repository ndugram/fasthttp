# Pydantic Validation

FastHTTP supports validation of requests and responses using Pydantic.

## Request Validation (request_model)

Request validation allows checking data before sending to the server. This is useful to avoid sending invalid data.

### Basic Example

```python
from pydantic import BaseModel, Field
from fasthttp import FastHTTP

app = FastHTTP()

class UserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    age: int = Field(ge=0, le=150)

@app.post(
    url="https://api.example.com/users",
    json={"name": "John", "email": "john@example.com", "age": 25},
    request_model=UserRequest
)
async def create_user(resp):
    return resp.json()
```

If data fails validation, the request is not sent.

### Validation with Error

```python
@app.post(
    url="https://api.example.com/users",
    json={"name": "", "email": "invalid", "age": 200},
    request_model=UserRequest
)
async def create_user(resp):
    return resp.json()

# Request won't be sent to server
# In logs: ERROR | Request validation failed: ...
```

### Form Data Validation

```python
class LoginForm(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=8)

@app.post(
    url="https://api.example.com/login",
    data={"username": "john", "password": "secret123"},
    request_model=LoginForm
)
async def login(resp):
    return resp.json()
```

### Custom Validators

```python
from pydantic import BaseModel, field_validator

class UserRequest(BaseModel):
    name: str
    email: str
    
    @field_validator('email')
    @classmethod
    def email_must_contain_at(cls, v):
        if '@' not in v:
            raise ValueError('Email must contain @')
        return v.lower()

@app.post(
    url="https://api.example.com/users",
    json={"name": "John", "email": "JOHN@EXAMPLE.COM"},
    request_model=UserRequest
)
async def create_user(resp):
    return resp.json()
```

## Response Validation (response_model)

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

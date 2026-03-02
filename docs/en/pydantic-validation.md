# Pydantic Validation

Validate API responses with Pydantic models.

## Basic Usage

```python
from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    email: str


@app.get(url="https://api.example.com/users/1", response_model=User)
async def get_user(resp):
    return resp.json()
```

## Field Constraints

```python
from pydantic import BaseModel, Field


class Post(BaseModel):
    id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=10)
```

## Nested Models

```python
from pydantic import BaseModel


class Address(BaseModel):
    street: str
    city: str


class User(BaseModel):
    id: int
    name: str
    address: Address
```

## Email Validation

```python
from pydantic import BaseModel, EmailStr


class User(BaseModel):
    name: str
    email: EmailStr
```

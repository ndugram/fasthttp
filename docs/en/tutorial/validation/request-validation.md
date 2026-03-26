# Request Validation

Validate request data before sending to the server.

## Using request_model

```python
from pydantic import BaseModel, Field
from fasthttp import FastHTTP


class UserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    age: int = Field(ge=0, le=150)


app = FastHTTP()


@app.post(
    url="https://api.example.com/users",
    json={"name": "John", "email": "john@example.com", "age": 25},
    request_model=UserRequest
)
async def create_user(resp):
    return resp.json()
```

If data fails validation, the request is not sent.

## Validation Failure

```python
# This request will NOT be sent
@app.post(
    url="https://api.example.com/users",
    json={"name": "", "email": "invalid", "age": 200},
    request_model=UserRequest
)
async def create_user(resp):
    return resp.json()

# In logs: ERROR | Request validation failed: ...
```

## Form Data Validation

```python
class LoginForm(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=8)


app = FastHTTP()


@app.post(
    url="https://api.example.com/login",
    data={"username": "john", "password": "secret123"},
    request_model=LoginForm
)
async def login(resp):
    return resp.json()
```

## Custom Validators

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


app = FastHTTP()


@app.post(
    url="https://api.example.com/users",
    json={"name": "John", "email": "JOHN@EXAMPLE.COM"},
    request_model=UserRequest
)
async def create_user(resp):
    return resp.json()
```

## Why Validate?

Request validation helps:

- Catch errors before sending
- Ensure data format is correct
- Validate constraints (length, pattern, range)
- Prevent invalid API calls

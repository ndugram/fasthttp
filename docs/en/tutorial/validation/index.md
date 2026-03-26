# Validation

FastHTTP supports validation of requests and responses using Pydantic.

## Overview

- [Response Validation](pydantic-validation.md) - Validate API responses
- [Request Validation](request-validation.md) - Validate data before sending
- [Error Validation](error-validation.md) - Handle API errors with Pydantic

## Quick Example

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


app.run()
```

FastHTTP automatically:
1. Receives JSON response
2. Validates against Pydantic model
3. Returns validated object

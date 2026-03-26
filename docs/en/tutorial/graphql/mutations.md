# GraphQL Mutations

Execute GraphQL mutations to write data.

## Basic Mutation

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.graphql(
    url="https://api.example.com/graphql",
    operation_type="mutation"
)
async def create_user(resp: Response) -> dict:
    return {
        "query": "mutation { createUser(name: $name) { id name } }",
        "variables": {"name": "John"}
    }
```

## Mutation with Multiple Fields

```python
@app.graphql(
    url="https://api.example.com/graphql",
    operation_type="mutation"
)
async def create_user(resp: Response) -> dict:
    return {
        "query": """
            mutation CreateUser($name: String!, $email: String!) {
                createUser(name: $name, email: $email) {
                    id
                    name
                    email
                }
            }
        """,
        "variables": {
            "name": "John Doe",
            "email": "john@example.com"
        }
    }
```

## Update Mutation

```python
@app.graphql(
    url="https://api.example.com/graphql",
    operation_type="mutation"
)
async def update_user(resp: Response) -> dict:
    return {
        "query": """
            mutation UpdateUser($id: ID!, $name: String!) {
                updateUser(id: $id, name: $name) {
                    id
                    name
                }
            }
        """,
        "variables": {"id": "1", "name": "Jane"}
    }
```

## Delete Mutation

```python
@app.graphql(
    url="https://api.example.com/graphql",
    operation_type="mutation"
)
async def delete_user(resp: Response) -> dict:
    return {
        "query": """
            mutation DeleteUser($id: ID!) {
                deleteUser(id: $id) {
                    success
                }
            }
        """,
        "variables": {"id": "1"}
    }
```

## With Dependencies

```python
from fasthttp import FastHTTP, Depends
from fasthttp.response import Response

app = FastHTTP()


async def add_auth(route, config):
    config.setdefault("headers", {})["Authorization"] = "Bearer my-token"
    return config


@app.graphql(
    url="https://api.example.com/graphql",
    operation_type="mutation",
    dependencies=[Depends(add_auth)]
)
async def create_user(resp: Response) -> dict:
    return {
        "query": "mutation { createUser(name: $name) { id } }",
        "variables": {"name": "John"}
    }
```

## With Validation

```python
from pydantic import BaseModel
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


class User(BaseModel):
    id: int
    name: str
    email: str


@app.graphql(
    url="https://api.example.com/graphql",
    operation_type="mutation",
    response_model=User
)
async def create_user(resp: Response) -> dict:
    return {
        "query": """
            mutation CreateUser($name: String!, $email: String!) {
                createUser(name: $name, email: $email) {
                    id
                    name
                    email
                }
            }
        """,
        "variables": {"name": "John", "email": "john@example.com"}
    }
```

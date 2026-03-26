# GraphQL мутации

Выполнение GraphQL мутаций для записи данных.

## Базовая мутация

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.graphql(url="https://api.example.com/graphql", operation_type="mutation")
async def create_user(resp: Response) -> dict:
    return {
        "query": "mutation { createUser(name: $name) { id name } }",
        "variables": {"name": "John"}
    }
```

## Мутация с несколькими полями

```python
@app.graphql(url="https://api.example.com/graphql", operation_type="mutation")
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
        "variables": {"name": "John Doe", "email": "john@example.com"}
    }
```

## С зависимостями

```python
from fasthttp import FastHTTP, Depends

async def add_auth(route, config):
    config.setdefault("headers", {})["Authorization"] = "Bearer my-token"
    return config


@app.graphql(url="https://api.example.com/graphql", operation_type="mutation",
    dependencies=[Depends(add_auth)])
async def create_user(resp: Response) -> dict:
    return {"query": "mutation { createUser(name: $name) { id } }",
        "variables": {"name": "John"}}

# GraphQL запросы

Выполнение GraphQL запросов.

## Базовый запрос

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.graphql(url="https://api.example.com/graphql")
async def get_user(resp: Response) -> dict:
    return {"query": "{ user(id: 1) { name email } }"}
```

## Запрос с переменными

```python
@app.graphql(url="https://api.example.com/graphql")
async def get_users(resp: Response) -> dict:
    return {
        "query": """
            query GetUsers($limit: Int!, $offset: Int!) {
                users(limit: $limit, offset: $offset) {
                    id
                    name
                    email
                }
            }
        """,
        "variables": {"limit": 10, "offset": 0}
    }
```

## С валидацией Pydantic

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str


@app.graphql(url="https://api.example.com/graphql", response_model=User)
async def get_user(resp: Response) -> dict:
    return {"query": "{ user(id: 1) { id name email } }"}
```

## С авторизацией

```python
@app.graphql(url="https://api.example.com/graphql",
    headers={"Authorization": "Bearer YOUR_TOKEN"})
async def get_profile(resp: Response) -> dict:
    return {"query": "{ me { name email } }"}

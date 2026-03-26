# GraphQL Queries

Execute GraphQL queries.

## Basic Query

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.graphql(url="https://api.example.com/graphql")
async def get_user(resp: Response) -> dict:
    return {"query": "{ user(id: 1) { name email } }"}
```

## Query with Variables

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
        "variables": {
            "limit": 10,
            "offset": 0
        }
    }
```

## Decorator Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `str` | - | GraphQL endpoint URL (required) |
| `operation_type` | `str` | `"query"` | Operation type |
| `headers` | `dict` | `None` | Additional headers |
| `timeout` | `float` | `30.0` | Request timeout |
| `tags` | `list` | `None` | Tags for grouping |
| `response_model` | `type` | `None` | Pydantic model |
| `dependencies` | `list` | `None` | Dependencies |

## Return Dictionary

Handler must return dict with:

| Key | Type | Description |
|-----|------|-------------|
| `query` | `str` | GraphQL query (required) |
| `variables` | `dict` | Query variables |
| `operation_name` | `str` | Operation name |

## With Pydantic Validation

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
    response_model=User
)
async def get_user(resp: Response) -> dict:
    return {"query": "{ user(id: 1) { id name email } }"}
```

## With Authorization

```python
@app.graphql(
    url="https://api.example.com/graphql",
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
async def get_profile(resp: Response) -> dict:
    return {"query": "{ me { name email } }"}
```

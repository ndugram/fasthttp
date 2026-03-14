# GraphQL

FastHTTP supports GraphQL queries and mutations through the `@app.graphql()` decorator.

## Introduction

GraphQL is a query language for APIs that allows clients to request exactly the data they need. FastHTTP provides a convenient decorator for working with GraphQL endpoints.

## Usage

### Query (reading data)

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.graphql(url="https://api.example.com/graphql")
async def get_user(resp: Response) -> dict:
    return {"query": "{ user(id: 1) { name email } }"}
```

### Mutation (writing data)

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

## Decorator Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `str` | — | GraphQL endpoint URL (required) |
| `operation_type` | `str` | `"query"` | Operation type: `"query"` or `"mutation"` |
| `headers` | `dict` | `None` | Additional headers |
| `timeout` | `float` | `30.0` | Request timeout in seconds |
| `tags` | `list` | `None` | Tags for grouping requests |
| `response_model` | `type[BaseModel]` | `None` | Pydantic model for response validation |
| `dependencies` | `list` | `None` | List of dependencies |

## Return Dictionary Parameters

The handler function must return a dictionary with the following keys:

| Key | Type | Description |
|-----|------|-------------|
| `query` | `str` | GraphQL query (required) |
| `variables` | `dict` | Query variables |
| `operation_name` | `str` | Operation name (if multiple) |

## Data Types

### GraphQLResponse

Represents the response from a GraphQL server:

```python
from fasthttp.graphql import GraphQLResponse

response = GraphQLResponse(
    data={"user": {"name": "John"}},
    errors=None,
    extensions={"traceId": "abc123"}
)

# Check for errors
if response.ok:
    print(response.data)
elif response.has_errors:
    print(response.errors)
```

**GraphQLResponse properties:**

| Property | Type | Description |
|----------|------|-------------|
| `data` | `dict \| None` | Response data |
| `errors` | `list \| None` | List of errors |
| `extensions` | `dict \| None` | Additional data |
| `ok` | `bool` | `True` if no errors |
| `has_errors` | `bool` | `True` if has errors |

## Examples

### Creating a user

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


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
        "variables": {
            "name": "John Doe",
            "email": "john@example.com"
        }
    }


if __name__ == "__main__":
    app.run()
```

### Getting a list with filtering

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


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

### With authorization

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.graphql(
    url="https://api.example.com/graphql",
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
async def get_profile(resp: Response) -> dict:
    return {"query": "{ me { name email } }"}
```

### Using with other methods

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.get(url="https://httpbin.org/get")
async def http_get(resp: Response) -> dict:
    return resp.json()


@app.graphql(url="https://api.example.com/graphql")
async def graphql_query(resp: Response) -> dict:
    return {"query": "{ version }"}


# Run both requests
app.run()

# Run only GraphQL
app.run(tags=["graphql"])
```

### With Pydantic Validation

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


# For list of objects
@app.graphql(
    url="https://api.example.com/graphql",
    response_model=list[User]
)
async def get_users(resp: Response) -> dict:
    return {"query": "{ users { id name email } }"}
```

### With Dependencies

```python
from fasthttp import FastHTTP, Depends
from fasthttp.response import Response

app = FastHTTP()


async def add_auth(route, config):
    config.setdefault("headers", {})["Authorization"] = "Bearer my-token"
    return config


async def add_trace_id(route, config):
    import uuid
    config.setdefault("headers", {})["X-Trace-ID"] = str(uuid.uuid4())
    return config


@app.graphql(
    url="https://api.example.com/graphql",
    operation_type="mutation",
    dependencies=[Depends(add_auth), Depends(add_trace_id)]
)
async def create_user(resp: Response) -> dict:
    return {
        "query": "mutation { createUser(name: $name) { id } }",
        "variables": {"name": "John"}
    }
```

### With Both response_model and Dependencies

```python
from pydantic import BaseModel
from fasthttp import FastHTTP, Depends
from fasthttp.response import Response

app = FastHTTP()


class User(BaseModel):
    id: int
    name: str
    email: str


async def add_auth(route, config):
    config.setdefault("headers", {})["Authorization"] = "Bearer my-token"
    return config


@app.graphql(
    url="https://api.example.com/graphql",
    response_model=User,
    dependencies=[Depends(add_auth)]
)
async def get_user(resp: Response) -> dict:
    return {"query": "{ user(id: 1) { id name email } }"}
```

## See also

- [Middleware](middleware.md) — for adding logic
- [Configuration](configuration.md) — settings
- [Quick Start](quick-start.md) — basics

# Tags

Tags allow grouping and filtering requests.

## Basic Usage

```python
from fasthttp import FastHTTP

app = FastHTTP()


@app.get(url="https://api.example.com/users", tags=["users"])
async def get_users(resp) -> dict:
    return resp.json()


@app.post(url="https://api.example.com/users", tags=["users"])
async def create_user(resp) -> dict:
    return resp.json()


@app.get(url="https://api.example.com/posts", tags=["posts"])
async def get_posts(resp) -> dict:
    return resp.json()


@app.post(url="https://api.example.com/posts", tags=["posts"])
async def create_post(resp) -> dict:
    return resp.json()
```

## Filtering by Tags

Run only requests with specific tags:

```python
# Run only users
app.run(tags=["users"])

# Run only posts
app.run(tags=["posts"])

# Run both users and posts
app.run(tags=["users", "posts"])
```

## Multiple Tags

A request can have multiple tags:

```python
@app.get(
    url="https://api.example.com/users",
    tags=["users", "v1", "api"]
)
async def get_users(resp) -> dict:
    return resp.json()
```

## Use Cases

### Development vs Production

```python
@app.get(url="https://dev.api.com/data", tags=["dev", "debug"])
async def dev_request(resp) -> dict:
    return resp.json()


@app.get(url="https://api.example.com/data", tags=["prod"])
async def prod_request(resp) -> dict:
    return resp.json()
```

### By Resource

```python
@app.get(url="https://api.example.com/users", tags=["users"])
async def get_users(resp) -> dict:
    return resp.json()


@app.get(url="https://api.example.com/orders", tags=["orders"])
async def get_orders(resp) -> dict:
    return resp.json()
```

### By Operation Type

```python
@app.get(url="https://api.example.com/users", tags=["read", "users"])
async def get_users(resp) -> dict:
    return resp.json()


@app.post(url="https://api.example.com/users", tags=["write", "users"])
async def create_user(resp) -> dict:
    return resp.json()
```

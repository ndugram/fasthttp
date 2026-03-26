# Request Parameters

Learn how to pass different types of data in requests.

## Query Parameters

Use the `params` parameter:

```python
@app.get(
    url="https://api.example.com/search",
    params={"q": "fasthttp", "page": 1, "limit": 10}
)
async def search(resp: Response) -> dict:
    return resp.json()

# Actual URL: https://api.example.com/search?q=fasthttp&page=1&limit=10
```

## JSON Body

Use the `json` parameter for POST, PUT, PATCH:

```python
@app.post(
    url="https://api.example.com/users",
    json={"name": "John", "email": "john@example.com", "age": 25}
)
async def create_user(resp: Response) -> dict:
    return resp.json()
```

## Raw Data

Use the `data` parameter for raw bytes:

```python
@app.post(
    url="https://api.example.com/upload",
    data=b"raw bytes data"
)
async def upload(resp: Response) -> dict:
    return resp.json()
```

## Headers

### Global Headers

```python
app = FastHTTP(
    get_request={
        "headers": {
            "Authorization": "Bearer my-secret-token",
            "User-Agent": "MyApp/1.0",
            "Accept": "application/json",
        }
    }
)
```

### Local Headers

```python
@app.get(
    url="https://api.example.com/data",
    get_request={
        "headers": {"X-Custom-Header": "value"}
    }
)
async def with_headers(resp: Response) -> dict:
    return resp.json()
```

## Form Data

Use `data` with dictionary:

```python
@app.post(
    url="https://api.example.com/login",
    data={"username": "john", "password": "secret123"}
)
async def login(resp: Response) -> dict:
    return resp.json()
```

## Combining Parameters

You can combine multiple parameters:

```python
@app.post(
    url="https://api.example.com/posts",
    params={"user_id": 1},  # Query parameters
    json={"title": "Hello"},  # JSON body
    get_request={
        "headers": {"Authorization": "Bearer token"}  # Headers
    }
)
async def create_post(resp: Response) -> dict:
    return resp.json()
```

## Timeout

Override timeout per request:

```python
@app.get(
    url="https://api.example.com/slow",
    timeout=120.0
)
async def slow_request(resp: Response) -> dict:
    return resp.json()
```

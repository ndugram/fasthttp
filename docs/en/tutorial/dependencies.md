# Dependencies

Dependencies allow modifying requests before sending.

## What Are Dependencies?

A dependency is a function that runs before each request and can modify the request configuration. This is useful for:

- Adding authentication headers
- Adding trace IDs
- Modifying request parameters
- Logging

## Basic Example

```python
from fasthttp import FastHTTP, Depends
from fasthttp.response import Response

app = FastHTTP()


async def add_auth(route, config):
    """Adds authorization token."""
    config.setdefault("headers", {})["Authorization"] = "Bearer my-token"
    return config


@app.get(
    url="https://api.example.com/protected",
    dependencies=[Depends(add_auth)]
)
async def protected_request(resp: Response) -> dict:
    return resp.json()
```

## Dependency Function Signature

A dependency function receives two parameters:

```python
async def my_dependency(route, config):
    # route - information about the request
    # config - request configuration
    
    # Modify config
    config["headers"]["X-Custom"] = "value"
    
    # Return modified config
    return config
```

### Route Attributes

```python
route.method      # HTTP method: "GET", "POST", etc.
route.url         # Full request URL
route.params      # Query parameters
route.json        # JSON body
route.data        # Raw data
route.tags        # Request tags
```

### Config Keys

```python
config.get("headers", {})      # Request headers
config.get("timeout", 30.0)    # Timeout in seconds
config.get("allow_redirects", True)
```

## Multiple Dependencies

Dependencies execute in order:

```python
async def add_auth(route, config):
    config.setdefault("headers", {})["Authorization"] = "Bearer token"
    return config


async def add_trace(route, config):
    config.setdefault("headers", {})["X-Trace-ID"] = "123"
    return config


@app.get(
    url="https://api.example.com/data",
    dependencies=[Depends(add_auth), Depends(add_trace)]
)
async def handler(resp: Response) -> dict:
    return resp.json()
```

## Use Cache

Use `use_cache` to cache expensive operations:

```python
async def get_token(route, config):
    # Expensive operation - fetch from auth server
    token = await fetch_token()
    config["headers"]["Authorization"] = f"Bearer {token}"
    return config


# Token will be obtained once and reused
@app.get(url="/api/data", dependencies=[Depends(get_token, use_cache=True)])
async def handler1(resp): ...


@app.get(url="/api/other", dependencies=[Depends(get_token, use_cache=True)])
async def handler2(resp): ...
```

## Practical Examples

### Dynamic Token

```python
import os


async def add_auth(route, config):
    token = os.getenv("API_TOKEN")
    config.setdefault("headers", {})["Authorization"] = f"Bearer {token}"
    return config
```

### Conditional Headers

```python
async def add_api_version(route, config):
    headers = config.setdefault("headers", {})
    
    if "/v2/" in route.url:
        headers["X-API-Version"] = "v2"
    else:
        headers["X-API-Version"] = "v1"
    
    return config
```

## Without Depends()

You can omit `Depends()`:

```python
# Both work the same
@app.get(url="/test1", dependencies=[Depends(add_auth)])
async def test1(resp): ...


@app.get(url="/test2", dependencies=[add_auth])
async def test2(resp): ...
```

## Comparison with Middleware

| Feature | Middleware | Dependencies |
|---------|------------|--------------|
| Global application | Yes | No |
| Specific request | No | Yes |
| Can modify response | Yes | No |
| Simpler to use | No | Yes |

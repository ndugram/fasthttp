# Dependencies Reference

Depends function reference.

## Depends()

Create a dependency:

```python
from fasthttp import Depends


def my_dependency(route, config):
    config.setdefault("headers", {})["X-Custom"] = "value"
    return config


# Usage
@app.get(url="/data", dependencies=[Depends(my_dependency)])
async def handler(resp):
    return resp.json()
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `func` | `Callable` | - | Dependency function |
| `use_cache` | `bool` | `True` | Cache result |
| `scope` | `str` | `"function"` | Execution scope |

## use_cache

If `True`, result is cached for request duration:

```python
async def get_token(route, config):
    token = await fetch_token()
    config["headers"]["Authorization"] = f"Bearer {token}"
    return config


# Token fetched once, reused
@app.get(url="/api/data", dependencies=[Depends(get_token, use_cache=True)])
async def handler1(resp): ...


@app.get(url="/api/other", dependencies=[Depends(get_token, use_cache=True)])
async def handler2(resp): ...
```

## scope

- `"function"` (default) - Before handler
- `"request"` - Around request-response cycle

```python
async def log_request(route, config):
    print(f"Request: {route.method} {route.url}")
    return config


@app.get(url="/data", dependencies=[Depends(log_request, scope="function")])
async def handler(resp): ...
```

## Without Depends()

You can omit `Depends()`:

```python
# Both work the same
@app.get(url="/test", dependencies=[Depends(add_auth)])
async def test1(resp): ...


@app.get(url="/test", dependencies=[add_auth])
async def test2(resp): ...
```

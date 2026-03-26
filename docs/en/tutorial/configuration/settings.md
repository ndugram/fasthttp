# Settings

Basic application configuration.

## Constructor Parameters

```python
from fasthttp import FastHTTP

app = FastHTTP(
    debug=False,      # Debug mode
    http2=False,      # Use HTTP/2
    proxy=None,       # Proxy server
    security=True,    # Enable security
    lifespan=None,    # Lifespan context manager
    middleware=[],    # Middleware list
    get_request={},   # Default GET settings
    post_request={},  # Default POST settings
    put_request={},   # Default PUT settings
    patch_request={}, # Default PATCH settings
    delete_request={} # Default DELETE settings
)
```

## Parameter Table

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `debug` | `bool` | `False` | Enable verbose logging |
| `http2` | `bool` | `False` | Use HTTP/2 |
| `proxy` | `str` | `None` | Proxy server URL |
| `security` | `bool` | `True` | Enable security features |
| `lifespan` | `Callable` | `None` | Startup/shutdown handler |
| `middleware` | `list` | `[]` | Middleware instances |
| `get_request` | `dict` | `{}` | Default GET settings |
| `post_request` | `dict` | `{}` | Default POST settings |
| `put_request` | `dict` | `{}` | Default PUT settings |
| `patch_request` | `dict` | `{}` | Default PATCH settings |
| `delete_request` | `dict` | `{}` | Default DELETE settings |

## Minimal Configuration

```python
from fasthttp import FastHTTP

app = FastHTTP()
```

## Full Configuration

```python
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware


class MyMiddleware(BaseMiddleware):
    pass


app = FastHTTP(
    debug=True,
    http2=False,
    proxy="http://proxy.example.com:8080",
    security=True,
    middleware=[MyMiddleware()],
    get_request={
        "headers": {"User-Agent": "MyApp/1.0"},
        "timeout": 30.0,
    },
    post_request={
        "headers": {"Content-Type": "application/json"},
        "timeout": 60.0,
    },
)
```

## Per-Method Settings

Each HTTP method can have its own defaults:

```python
app = FastHTTP(
    get_request={
        "headers": {"Accept": "application/json"},
        "timeout": 30.0,
    },
    post_request={
        "headers": {"Content-Type": "application/json"},
        "timeout": 60.0,
    },
    put_request={
        "headers": {"Content-Type": "application/json"},
        "timeout": 60.0,
    },
    delete_request={
        "headers": {"Accept": "application/json"},
        "timeout": 30.0,
    },
)
```

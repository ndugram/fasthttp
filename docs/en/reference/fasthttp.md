# FastHTTP Class

Main application class reference.

## Constructor

```python
from fasthttp import FastHTTP

app = FastHTTP(
    debug: bool = False,
    http2: bool = False,
    proxy: str = None,
    security: bool = True,
    lifespan: Callable = None,
    middleware: list = [],
    get_request: dict = {},
    post_request: dict = {},
    put_request: dict = {},
    patch_request: dict = {},
    delete_request: dict = {},
)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `debug` | `bool` | `False` | Enable debug mode |
| `http2` | `bool` | `False` | Use HTTP/2 |
| `proxy` | `str` | `None` | Proxy server URL |
| `security` | `bool` | `True` | Enable security |
| `lifespan` | `Callable` | `None` | Startup/shutdown handler |
| `middleware` | `list` | `[]` | Middleware list |
| `get_request` | `dict` | `{}` | Default GET settings |
| `post_request` | `dict` | `{}` | Default POST settings |
| `put_request` | `dict` | `{}` | Default PUT settings |
| `patch_request` | `dict` | `{}` | Default PATCH settings |
| `delete_request` | `dict` | `{}` | Default DELETE settings |

## Methods

### run()

Execute all registered requests.

```python
app.run(tags: list = None)
```

**Parameters:**
- `tags` - Filter requests by tags

**Example:**

```python
app.run()           # Run all
app.run(tags=["users"])  # Run only users
```

### web_run()

Run with Swagger UI.

```python
app.web_run(host: str = "127.0.0.1", port: int = 8000)
```

**Parameters:**
- `host` - Host to bind
- `port` - Port to bind

### get()

Decorator for GET requests.

```python
@app.get(
    url: str,
    params: dict = None,
    tags: list = [],
    dependencies: list = [],
    response_model: type = None,
    request_model: type = None,
    responses: dict = None,
)
```

### post()

Decorator for POST requests.

### put()

Decorator for PUT requests.

### patch()

Decorator for PATCH requests.

### delete()

Decorator for DELETE requests.

### graphql()

Decorator for GraphQL.

```python
@app.graphql(
    url: str,
    operation_type: str = "query",
    headers: dict = None,
    timeout: float = 30.0,
    tags: list = [],
    response_model: type = None,
    dependencies: list = None,
)
```

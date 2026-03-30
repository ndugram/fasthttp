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
    base_url: str = None,
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
| `base_url` | `str` | `None` | Default base URL for decorators and routers |
| `get_request` | `dict` | `{}` | Default GET settings |
| `post_request` | `dict` | `{}` | Default POST settings |
| `put_request` | `dict` | `{}` | Default PUT settings |
| `patch_request` | `dict` | `{}` | Default PATCH settings |
| `delete_request` | `dict` | `{}` | Default DELETE settings |

**base_url Usage:**

```python
app = FastHTTP(base_url="https://api.example.com")

@app.get("/users")      # → https://api.example.com/users
@app.post("/users")     # → https://api.example.com/users

@app.get("https://other.com/api")  # → https://other.com/api (absolute URL)
```

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
app.web_run(host: str = "127.0.0.1", port: int = 8000, base_url: str = "")
```

**Parameters:**
- `host` - Host to bind
- `port` - Port to bind
- `base_url` - Optional docs URL prefix, for example `"/api"`

### include_router()

Include a `Router` into the application.

```python
app.include_router(
    router: Router,
    prefix: str = "",
    tags: list = None,
    dependencies: list = None,
    base_url: str = None,
)
```

**Parameters:**
- `router` - Router instance to include
- `prefix` - Optional prefix added before the router prefix
- `tags` - Optional tags added before router tags
- `dependencies` - Optional dependencies added before router dependencies
- `base_url` - Optional base URL override for the included router tree

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

## Router

`Router` is available from:

```python
from fasthttp import Router
```

Basic constructor:

```python
Router(
    base_url: str = None,
    prefix: str = "",
    tags: list = None,
    dependencies: list = None,
)
```

See the tutorial page for examples:
- `docs/en/tutorial/routers.md`

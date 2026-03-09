# API Reference

Complete reference for all FastHTTP classes and functions.

## FastHTTP Class

The main application class.

```python
from fasthttp import FastHTTP
```

### Constructor

```python
app = FastHTTP(
    debug: bool = False,
    http2: bool = False,
    get_request: dict = {},
    post_request: dict = {},
    put_request: dict = {},
    patch_request: dict = {},
    delete_request: dict = {},
    middleware: list = [],
    security: bool = True,
    lifespan: Callable = None,
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `debug` | `bool` | `False` | Debug mode |
| `http2` | `bool` | `False` | Use HTTP/2 |
| `get_request` | `dict` | `{}` | GET settings |
| `post_request` | `dict` | `{}` | POST settings |
| `put_request` | `dict` | `{}` | PUT settings |
| `patch_request` | `dict` | `{}` | PATCH settings |
| `delete_request` | `dict` | `{}` | DELETE settings |
| `middleware` | `list` | `[]` | Middleware list |
| `security` | `bool` | `True` | Enable built-in security |
| `lifespan` | `Callable` | `None` | Context manager for startup/shutdown |

### Methods

#### run()

Starts executing requests.

```python
app.run(
    tags: list = None,
)
```

**Parameters:**
- `tags` — list of tags to filter requests

**Example:**

```python
app.run()  # Run all
app.run(tags=["users"])  # Only with tag users
```

### Lifespan

Context manager for running code before and after requests.

```python
from contextlib import asynccontextmanager
from fasthttp import FastHTTP

@asynccontextmanager
async def lifespan(app: FastHTTP):
    # Startup
    app.token = await load_token()
    yield
    # Shutdown
    await cleanup()

app = FastHTTP(lifespan=lifespan)
```

**Parameters:**
- `app` — FastHTTP instance, can add attributes

**Usage examples:**

```python
# Load configuration
@asynccontextmanager
async def lifespan(app):
    app.config = load_config()
    yield

# Connect to Redis
@asynccontextmanager
async def lifespan(app):
    app.redis = await aioredis.from_url("redis://localhost")
    yield
    await app.redis.close()

# Collect statistics
@asynccontextmanager
async def lifespan(app):
    app.stats = {"requests": 0}
    yield
    print(f"Total: {app.stats['requests']} requests")
```

## HTTP Method Decorators

### @app.get()

```python
@app.get(
    url: str,
    params: dict = None,
    tags: list = [],
    dependencies: list = [],
    response_model: type = None,
    request_model: type = None,
    get_request: dict = None,
)
```

### @app.post()

```python
@app.post(
    url: str,
    json: dict = None,
    data: bytes = None,
    params: dict = None,
    tags: list = [],
    dependencies: list = [],
    response_model: type = None,
    request_model: type = None,
    post_request: dict = None,
)
```

### @app.put()

```python
@app.put(
    url: str,
    json: dict = None,
    data: bytes = None,
    params: dict = None,
    tags: list = [],
    dependencies: list = [],
    response_model: type = None,
    request_model: type = None,
    put_request: dict = None,
)
```

### @app.patch()

```python
@app.patch(
    url: str,
    json: dict = None,
    data: bytes = None,
    params: dict = None,
    tags: list = [],
    dependencies: list = [],
    response_model: type = None,
    request_model: type = None,
    patch_request: dict = None,
)
```

### @app.delete()

```python
@app.delete(
    url: str,
    params: dict = None,
    tags: list = [],
    dependencies: list = [],
    response_model: type = None,
    request_model: type = None,
    delete_request: dict = None,
)
```

### Decorator Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | `str` | Request URL |
| `params` | `dict` | Query parameters |
| `json` | `dict` | JSON request body |
| `data` | `bytes` | Raw request data |
| `tags` | `list` | Tags for grouping |
| `dependencies` | `list` | Dependencies |
| `response_model` | `type[BaseModel]` | Pydantic model for response validation |
| `request_model` | `type[BaseModel]` | Pydantic model for request validation |

## Dependencies

### Depends()

```python
from fasthttp import Depends
```

Creates a dependency for modifying the request.

```python
Depends(
    func: Callable,
    use_cache: bool = True,
    scope: str = "function",
)
```

**Parameters:**
- `func` — async function with signature `(route, config) -> config`
- `use_cache` — cache result
- `scope` — scope ("function" or "request")

**Example:**

```python
async def add_auth(route, config):
    config.setdefault("headers", {})["Authorization"] = "Bearer token"
    return config

@app.get(url="/data", dependencies=[Depends(add_auth)])
async def handler(resp):
    return resp.json()
```

## Middleware

### BaseMiddleware

Base class for creating middleware.

```python
from fasthttp.middleware import BaseMiddleware

class MyMiddleware(BaseMiddleware):
    async def before_request(self, route, config):
        return config
    
    async def after_response(self, response, route, config):
        return response
    
    async def on_error(self, error, route, config):
        raise error
```

### CacheMiddleware

Built-in middleware for caching.

```python
from fasthttp import CacheMiddleware

app = FastHTTP(
    middleware=[CacheMiddleware(ttl=3600, max_size=100)]
)
```

**Parameters:**
- `ttl` — cache time-to-live in seconds
- `max_size` — maximum number of cached requests

## Response

The response object.

```python
@app.get(url="https://api.example.com/data")
async def handler(resp: Response):
    # Available attributes
    status = resp.status       # Status code (int)
    text = resp.text           # Response text (str)
    json_data = resp.json()    # JSON data (dict/list)
    headers = resp.headers     # Response headers (dict)
    content = resp.content     # Raw bytes (bytes)
```

## CLI

### fasthttp

```bash
fasthttp <method> <url> [options]
```

**Methods:** `get`, `post`, `put`, `patch`, `delete`

**Options:**

| Option | Description |
|--------|-------------|
| `-H, --header` | Header |
| `-p, --param` | Query parameter |
| `--json` | JSON body |
| `--timeout` | Timeout |
| `--debug` | Debug mode |
| `-o, --output` | Save to file |
| `--format` | Output format |

## Data Types

### Route

Object with route information:

```python
route.method          # HTTP method
route.url             # URL
route.params          # Query parameters
route.json            # JSON body
route.data            # Raw data
route.tags            # Tags
route.dependencies   # Dependencies
```

### Config

Dictionary with request configuration:

```python
config.get("headers", {})       # Headers
config.get("timeout", 30.0)      # Timeout
config.get("allow_redirects", True)  # Redirects
```

## Security

FastHTTP has built-in security system that works automatically.

### security parameter

```python
app = FastHTTP(security=True)   # Security enabled (default)
app = FastHTTP(security=False)  # Security disabled
```

### What's included

- **SSRF protection** — blocks requests to localhost and private IPs
- **Secrets masking** — hides Authorization, Cookie in logs
- **Circuit Breaker** — auto-blocks failing hosts
- **Limits** — timeout, max response size, max concurrent requests
- **Header protection** — removes CRLF characters
- **Redirect protection** — blocks file://, javascript:, internal IPs

### Example

```python
from fasthttp import FastHTTP

app = FastHTTP()  # security=True by default

@app.get(url="https://api.example.com/data")
async def handler(resp):
    return resp.json()

app.run()  # Security works automatically
```

See [Security](security.md) for details.

## See Also

- [Quick Start](quick-start.md) — basics
- [Configuration](configuration.md) — settings
- [Dependencies](dependencies.md) — request modification
- [Middleware](middleware.md) — global logic

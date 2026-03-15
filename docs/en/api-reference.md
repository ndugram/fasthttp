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
    responses: dict = None,
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
    responses: dict = None,
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
    responses: dict = None,
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
    responses: dict = None,
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
    responses: dict = None,
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
| `responses` | `dict[int, dict[Literal["model"], type[BaseModel]]]` | Pydantic models for API error validation |

### Type Annotation Requirements

FastHTTP requires all handler functions to have explicit type annotations:

1. **Parameter annotations** — each parameter must have a type
2. **Return type annotation** — function must return a specific type

**Correct function example:**

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()

@app.get(url="https://api.example.com/data")
async def get_data(resp: Response) -> dict:  # ✅ Annotations present
    return resp.json()
```

**Error examples:**

```python
# ❌ Missing parameter annotation
@app.get(url="https://api.example.com/data")
async def get_data(resp) -> dict:
    return resp.json()

# ❌ Missing return type annotation
@app.get(url="https://api.example.com/data")
async def get_data(resp: Response):
    return resp.json()

# ❌ Both annotations missing
@app.get(url="https://api.example.com/data")
async def get_data(resp):
    return resp.json()
```

**Errors when annotations are missing:**

```
TypeError: Parameter 'resp' in function 'get_data' must have a type annotation
TypeError: Function 'get_data' must explicitly define return type annotation
```

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

The Response object represents the HTTP response from the server. It contains all information about the response including status code, body, and headers.

### Response Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `status` | `int` | HTTP status code (e.g., 200, 404, 500) |
| `text` | `str` | Raw response body as string |
| `headers` | `dict` | Response headers as key-value pairs |
| `method` | `str` | HTTP method used for the request |

### Response Methods

The Response class provides several methods to work with the response data:

#### json()

Parses the response body as JSON and returns a Python dictionary or list.

```python
@app.get(url="https://api.example.com/data")
async def handler(resp: Response):
    data = resp.json()  # Returns dict or list
    return data
```

Raises `ValueError` if the response body is not valid JSON.

#### req_json()

Returns the JSON data that was sent with the request (if any).

```python
@app.post(url="https://api.example.com/data", json={"name": "John"})
async def handler(resp: Response):
    sent_data = resp.req_json()  # Returns {"name": "John"}
    return sent_data
```

#### req_text()

Returns the request body as a string.

```python
@app.post(url="https://api.example.com/data", data=b"raw data")
async def handler(resp: Response):
    sent_data = resp.req_text()  # Returns "raw data"
    return sent_data
```

### Complete Example

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)


@app.get(url="https://api.example.com/data")
async def handler(resp: Response) -> dict:
    # Access status code
    status = resp.status  # e.g., 200

    # Get response body as text
    body_text = resp.text  # Raw string

    # Parse JSON response
    json_data = resp.json()  # dict or list

    # Access response headers
    headers = resp.headers  # {"Content-Type": "application/json", ...}

    # Access request details
    req_headers = resp.req_headers  # Headers sent with request
    query_params = resp.query       # Query parameters used
    req_json = resp.req_json()      # JSON sent with request (if any)

    return {
        "status": status,
        "data": json_data,
        "headers": headers,
    }


if __name__ == "__main__":
    app.run()
```

### Response Properties

Additional properties available on Response:

```python
# HTTP method of the request (GET, POST, etc.)
resp.method

# Query parameters that were used
resp.query  # {"page": 1, "limit": 10}

# Request headers that were sent
resp.req_headers  # {"Authorization": "Bearer ..."}

# Request JSON body (if any)
resp.req_json()  # {"name": "John"}

# Request data as text
resp.req_text()  # "raw string"
```

### Empty Response Handling

When a request fails (e.g., 4xx or 5xx status), FastHTTP returns `None`. Always handle this case:

```python
@app.get(url="https://api.example.com/data")
async def handler(resp: Response) -> dict | None:
    if resp is None:
        return {"error": "Request failed"}

    return {"status": resp.status, "data": resp.json()}
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

The Route object represents a registered HTTP request. It contains all information about the request that FastHTTP will execute. This object is passed to middleware and dependencies so they can inspect and modify the request.

#### Route Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `method` | `str` | HTTP method (GET, POST, PUT, PATCH, DELETE) |
| `url` | `str` | Full URL of the request |
| `params` | `dict` | Query parameters |
| `json` | `dict` | JSON body sent with request |
| `data` | `bytes` | Raw data sent with request |
| `tags` | `list` | Tags for grouping requests |
| `dependencies` | `list` | List of dependencies |
| `response_model` | `type` | Pydantic model for response validation |
| `request_model` | `type` | Pydantic model for request validation |
| `handler` | `Callable` | The handler function |
| `skip_request` | `bool` | If True, skip actual HTTP request (for GraphQL) |

#### Example: Using Route in Middleware

```python
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware

class DebugMiddleware(BaseMiddleware):
    async def before_request(self, route, config):
        # Inspect the route
        print(f"Method: {route.method}")
        print(f"URL: {route.url}")
        print(f"Tags: {route.tags}")
        print(f"Has JSON: {route.json is not None}")

        # Can modify params
        if route.params:
            route.params["debug"] = "true"

        return config


app = FastHTTP(middleware=[DebugMiddleware()])


@app.get(url="https://api.example.com/data", params={"page": 1})
async def handler(resp):
    return resp.json()
```

### Config

The Config dictionary contains request configuration that can be modified by middleware and dependencies. It controls how the HTTP request is sent.

#### Config Keys

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `headers` | `dict` | `{}` | HTTP headers to send |
| `timeout` | `float` | `30.0` | Request timeout in seconds |
| `allow_redirects` | `bool` | `True` | Whether to follow redirects |

#### Example: Modifying Config in Dependency

```python
from fasthttp import FastHTTP, Depends

app = FastHTTP()


async def add_auth_token(route, config):
    """Add authentication header to all requests."""
    # Get existing headers or empty dict
    headers = config.get("headers", {})

    # Add authorization
    headers["Authorization"] = "Bearer my-secret-token"

    # Update config
    config["headers"] = headers

    # Can also modify timeout
    config["timeout"] = 60.0

    return config


async def add_debug_header(route, config):
    """Add debug header for specific URLs."""
    if "api.example.com" in route.url:
        config.setdefault("headers", {})["X-Debug"] = "true"

    return config


@app.get(
    url="https://api.example.com/data",
    dependencies=[Depends(add_auth_token), Depends(add_debug_header)]
)
async def handler(resp):
    return resp.json()
```

#### Accessing Config in Middleware

```python
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware

class MetricsMiddleware(BaseMiddleware):
    async def before_request(self, route, config):
        # Store start time in config for later use
        import time
        config["_start_time"] = time.time()

        # Check if custom timeout is set
        timeout = config.get("timeout", 30.0)
        print(f"Request timeout: {timeout}s")

        return config

    async def after_response(self, response, route, config):
        # Calculate duration
        import time
        duration = time.time() - config.get("_start_time", time.time())

        print(f"Request to {route.url} took {duration:.2f}s")
        return response


app = FastHTTP(middleware=[MetricsMiddleware()])
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

## GraphQL

### @app.graphql()

Decorator for executing GraphQL queries and mutations.

```python
@app.graphql(
    url: str,
    operation_type: str = "query",
    headers: dict = None,
    timeout: float = 30.0,
    tags: list = [],
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `str` | — | GraphQL endpoint (required) |
| `operation_type` | `str` | `"query"` | `"query"` or `"mutation"` |
| `headers` | `dict` | `None` | Additional headers |
| `timeout` | `float` | `30.0` | Request timeout in seconds |
| `tags` | `list` | `None` | Tags for grouping |

**Query Example:**

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.graphql(url="https://api.example.com/graphql")
async def get_user(resp: Response) -> dict:
    return {"query": "{ user(id: 1) { name email } }"}
```

**Mutation Example:**

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.graphql(url="https://api.example.com/graphql", operation_type="mutation")
async def create_user(resp: Response) -> dict:
    return {
        "query": "mutation { createUser(name: $name) { id } }",
        "variables": {"name": "John"}
    }
```

### GraphQLResponse

Represents response from GraphQL server.

```python
from fasthttp.graphql import GraphQLResponse

response = GraphQLResponse(
    data: dict = None,
    errors: list = None,
    extensions: dict = None,
)
```

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `data` | `dict \| None` | Response data |
| `errors` | `list \| None` | List of errors |
| `extensions` | `dict \| None` | Additional data |
| `ok` | `bool` | `True` if no errors |
| `has_errors` | `bool` | `True` if has errors |

## See Also

- [Quick Start](quick-start.md) — basics
- [Configuration](configuration.md) — settings
- [Dependencies](dependencies.md) — request modification
- [Middleware](middleware.md) — global logic
- [GraphQL](graphql.md) — detailed documentation

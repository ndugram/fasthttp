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
    query_request: dict = {},
    post_request: dict = {},
    put_request: dict = {},
    patch_request: dict = {},
    delete_request: dict = {},
    concurrency: int = None,
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
| `query_request` | `dict` | `{}` | Default QUERY settings |
| `post_request` | `dict` | `{}` | Default POST settings |
| `put_request` | `dict` | `{}` | Default PUT settings |
| `patch_request` | `dict` | `{}` | Default PATCH settings |
| `delete_request` | `dict` | `{}` | Default DELETE settings |
| `concurrency` | `int \| None` | `None` | Max parallel requests during `run()`. `None` = unlimited |

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

### query()

Decorator for QUERY requests. Safe and idempotent like GET, but accepts a `json`/`data` body (like POST).

```python
@app.query(
    url: str,
    json: dict = None,
    data: bytes = None,
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

### exception_handler()

Decorator registering a handler for a specific exception type, FastAPI-style. The handler's return value replaces the route's result instead of the request failing silently.

```python
@app.exception_handler(
    exc_type: type[Exception],
)
```

**Parameters:**
- `exc_type` - exception class this handler should be invoked for

**Handler signature:** `async def handler(route, exc) -> Any`

**Example:**

```python
from fasthttp.exceptions import FastHTTPTimeoutError

@app.exception_handler(FastHTTPTimeoutError)
async def handle_timeout(route, exc):
    return {"error": "timeout", "url": route.url}
```

Also available on `Router` via `@router.exception_handler(...)`. See [Event Hooks](../middleware.md#event-hooks) for `on_request`, `on_response`, `on_error`, and MRO-based dispatch details.

## AsyncSession

Imperative async HTTP client — like `httpx.AsyncClient`. Returns responses directly instead of logging them.

```python
from fasthttp import AsyncSession
```

### Constructor

```python
AsyncSession(
    base_url: str = None,
    headers: dict = None,
    timeout: float = 30.0,
    http2: bool = False,
    proxy: str = None,
    security: bool = True,
    middleware: list = None,
    cookie_jar: CookieJar = None,
    debug: bool = False,
    secret_key: bytes = None,
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base_url` | `str` | `None` | Base URL prepended to relative paths |
| `headers` | `dict` | `None` | Session-level headers sent with every request |
| `timeout` | `float` | `30.0` | Default timeout in seconds |
| `http2` | `bool` | `False` | Enable HTTP/2 |
| `proxy` | `str` | `None` | Proxy server URL |
| `security` | `bool` | `True` | Enable built-in security |
| `middleware` | `list` | `None` | Middleware applied to all requests |
| `cookie_jar` | `CookieJar` | `None` | Cookie jar for automatic cookie handling |
| `debug` | `bool` | `False` | Enable debug logging |
| `secret_key` | `bytes` | `None` | HMAC signing key (auto-generated if not set) |

### Methods

| Method | Signature |
|--------|-----------|
| `get` | `(url, *, params, headers, timeout) → Response \| None` |
| `query` | `(url, *, json, data, headers, timeout) → Response \| None` |
| `post` | `(url, *, json, data, headers, timeout) → Response \| None` |
| `put` | `(url, *, json, data, headers, timeout) → Response \| None` |
| `patch` | `(url, *, json, data, headers, timeout) → Response \| None` |
| `delete` | `(url, *, json, data, headers, timeout) → Response \| None` |
| `head` | `(url, *, params, headers, timeout) → Response \| None` |
| `options` | `(url, *, params, headers, timeout) → Response \| None` |
| `request` | `(method, url, *, params, json, data, headers, timeout) → Response \| None` |
| `open` | `() → None` — open connection pool |
| `close` | `() → None` — close connection pool |

### Example

```python
import asyncio
from fasthttp import AsyncSession


async def main():
    async with AsyncSession(
        base_url="https://api.example.com",
        headers={"Authorization": "Bearer token"},
    ) as session:
        resp = await session.get("/users")
        if resp:
            print(resp.json())


asyncio.run(main())
```

See the full tutorial: [AsyncSession](../tutorial/async-session.md)

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

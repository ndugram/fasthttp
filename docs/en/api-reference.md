# API Reference

Complete reference for FastHTTP client.

## FastHTTP Class

Main class for creating HTTP requests.

```python
from fasthttp import FastHTTP

app = FastHTTP(
    debug=False,      # Enable debug logging
    http2=False,      # Enable HTTP/2
    middleware=None,  # Middleware instance(s)
)
```

### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `debug` | `bool` | `False` | Enable detailed logging |
| `http2` | `bool` | `False` | Use HTTP/2 protocol |
| `middleware` | `BaseMiddleware` / `list` | `None` | Middleware to apply |
| `get_request` | `dict` | `None` | Default GET config |
| `post_request` | `dict` | `None` | Default POST config |
| `put_request` | `dict` | `None` | Default PUT config |
| `patch_request` | `dict` | `None` | Default PATCH config |
| `delete_request` | `dict` | `None` | Default DELETE config |

### Methods

#### `.get()`

Register a GET request:

```python
@app.get(url="https://api.example.com/users", params={"page": 1})
async def get_users(resp: Response):
    return resp.json()
```

**Parameters:**
- `url` — target URL (required)
- `params` — query parameters (optional)
- `response_model` — Pydantic model for validation (optional)

#### `.post()`

Register a POST request:

```python
@app.post(url="https://api.example.com/users", json={"name": "John"})
async def create_user(resp: Response):
    return resp.status
```

**Parameters:**
- `url` — target URL (required)
- `json` — JSON body (optional)
- `data` — form data (optional)
- `params` — query parameters (optional)
- `response_model` — Pydantic model for validation (optional)

#### `.put()` / `.patch()` / `.delete()`

Same parameters as `.post()`.

#### `.run()`

Execute all registered requests:

```python
if __name__ == "__main__":
    app.run()
```

## Response Class

Represents HTTP response.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `status` | `int` | HTTP status code (200, 404, etc.) |
| `text` | `str` | Raw response body |
| `headers` | `dict` | Response headers |

### Methods

#### `.json()`

Parse response body as JSON:

```python
data = resp.json()
# Returns: dict, list, or primitive

# Raises json.JSONDecodeError if invalid
```

**Returns:** Parsed JSON (dict, list, int, str, etc.)

## Request Configuration

Default configuration for each HTTP method:

```python
app = FastHTTP(
    get_request={
        "headers": {"User-Agent": "MyApp/1.0"},
        "timeout": 30,
        "allow_redirects": True,
    },
)
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `headers` | `dict` | `{}` | Request headers |
| `timeout` | `int` | `30` | Request timeout (seconds) |
| `allow_redirects` | `bool` | `True` | Follow redirects |

### Global vs Per-Request

Global config applies to all requests of that method:

```python
app = FastHTTP(
    get_request={"timeout": 10},  # All GET requests use 10s timeout
)
```

Per-request params merge with global config:

```python
@app.get(url="https://api.example.com/slow", params={"page": 1})
async def slow_request(resp):
    # Uses global timeout: 10s
    return resp.json()
```

## Middleware

Intercept and modify requests/responses.

```python
from fasthttp.middleware import BaseMiddleware


class MyMiddleware(BaseMiddleware):
    async def before_request(self, route, config):
        """Called before request is sent"""
        # Modify headers, add auth, etc.
        headers = config.get("headers", {})
        headers["X-Custom"] = "value"
        config["headers"] = headers
        return config

    async def after_response(self, response, route, config):
        """Called after response received"""
        # Modify response, log, cache, etc.
        return response

    async def on_error(self, error, route, config):
        """Called when error occurs"""
        # Log error, notify, etc.
        pass
```

### Using Middleware

```python
# Single middleware
app = FastHTTP(middleware=MyMiddleware())

# Multiple middleware (executed in order)
app = FastHTTP(middleware=[
    AuthMiddleware(),
    LoggingMiddleware(),
])
```

## Error Handling

All errors are caught and logged automatically.

### Error Types

| Error | Description |
|-------|-------------|
| `FastHTTPConnectionError` | Connection failed |
| `FastHTTPTimeoutError` | Request timed out |
| `FastHTTPBadStatusError` | HTTP 4xx/5xx status |

### Manual Raise

```python
from fasthttp.exceptions import FastHTTPBadStatusError


@app.get(url="https://api.example.com/data")
async def get_data(resp: Response):
    if resp.status == 404:
        raise FastHTTPBadStatusError(
            "Data not found",
            url="https://api.example.com/data",
            status_code=404
        )
    return resp.json()
```

## Logging

### Default (Info)

Shows status and timing:

```
✔ GET https://api.example.com [200] 234.56ms
✔ POST https://api.example.com/users [201] 89.12ms
```

### Debug Mode

```python
app = FastHTTP(debug=True)
```

Shows:
- Registered routes
- Request headers
- Response headers
- Response body
- Handler results

## Performance

All registered requests execute concurrently using asyncio:

```python
app = FastHTTP()


@app.get(url="https://api.example.com/users")
async def get_users(resp):
    return resp.json()


@app.get(url="https://api.example.com/posts")
async def get_posts(resp):
    return resp.json()


app.run()  # Both requests run in parallel
```

Small delay (0.5s) between requests prevents server overload.

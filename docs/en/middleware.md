# Middleware

Middleware lets you intercept and modify requests/responses. Use it for authentication, logging, caching, etc.

## Create Middleware

Inherit from `BaseMiddleware` and override methods you need:

```python
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware
from fasthttp.response import Response


class MyMiddleware(BaseMiddleware):
    async def before_request(self, route, config):
        """Called before request is sent"""
        # Modify request config (headers, timeout, etc.)
        return config

    async def after_response(self, response, route, config):
        """Called after response received"""
        # Modify or log response
        return response

    async def on_error(self, error, route, config):
        """Called when error occurs"""
        # Handle error (log, notify, etc.)
        pass
```

### Method Parameters

- `route` — Route object with method, url, handler info
- `config` — request configuration dict
- `response` — Response object
- `error` — Exception that occurred

## Usage

```python
app = FastHTTP(middleware=MyMiddleware())
```

Multiple middleware — executed in order:

```python
app = FastHTTP(middleware=[
    AuthMiddleware(),
    LoggingMiddleware(),
    ErrorTrackingMiddleware(),
])
```

Execution order:
1. `before_request` — first middleware to last
2. `after_response` — last middleware to first
3. `on_error` — first to last

## Examples

### Authentication

Add Bearer token to all requests:

```python
class AuthMiddleware(BaseMiddleware):
    def __init__(self, token: str):
        self.token = token

    async def before_request(self, route, config):
        headers = config.get("headers", {})
        headers["Authorization"] = f"Bearer {self.token}"
        config["headers"] = headers
        return config
```

### Request ID

Add unique ID for tracing:

```python
import uuid


class RequestIDMiddleware(BaseMiddleware):
    async def before_request(self, route, config):
        headers = config.get("headers", {})
        headers["X-Request-ID"] = str(uuid.uuid4())
        config["headers"] = headers
        return config
```

### Logging

Log all requests and responses:

```python
class LoggingMiddleware(BaseMiddleware):
    async def before_request(self, route, config):
        print(f"→ {route.method} {route.url}")
        return config

    async def after_response(self, response, route, config):
        print(f"← {route.method} {route.url} [{response.status}]")
        return response
```

### Error Tracking

```python
class ErrorTrackingMiddleware(BaseMiddleware):
    async def on_error(self, error, route, config):
        print(f"✗ {route.method} {route.url} failed: {error}")
```

### Caching

Built-in CacheMiddleware stores responses in memory:

```python
from fasthttp import CacheMiddleware

app = FastHTTP(middleware=[
    CacheMiddleware(ttl=3600, max_size=100)  # 1 hour, 100 items
])
```

How it works:
1. First request → goes to server → saved to cache
2. Subsequent requests (within TTL) → returns from cache
3. After TTL expires → new request to server

Only GET requests are cached.

## Best Practices

1. Keep middleware focused on single responsibility
2. Always return the modified config/response
3. Use `__init__` for configuration (token, settings)
4. Handle errors in `on_error` method

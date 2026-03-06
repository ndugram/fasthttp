# Middleware

Middleware allows adding global logic that will be executed for all requests.

## Introduction

Middleware in FastHTTP works similarly to middleware in FastAPI, but is designed for outgoing requests. It allows:

- Modifying requests before sending
- Modifying responses after receiving
- Handling errors
- Adding logging
- Adding authentication

## Creating Middleware

Create a class inheriting from `BaseMiddleware`:

```python
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware
from fasthttp.response import Response


class MyMiddleware(BaseMiddleware):
    async def before_request(self, route, config):
        """Executed before each request."""
        # Modify config
        config.setdefault("headers", {})["X-Custom"] = "value"
        return config

    async def after_response(self, response, route, config):
        """Executed after each response."""
        # Modify response
        return response

    async def on_error(self, error, route, config):
        """Executed on error."""
        print(f"Error: {error}")
        raise error
```

## Using Middleware

```python
from fasthttp import FastHTTP

app = FastHTTP(middleware=MyMiddleware())
```

### Multiple Middleware

Execution order — first added executes first:

```python
app = FastHTTP(middleware=[
    AuthMiddleware(),
    LoggingMiddleware(),
    MetricsMiddleware(),
])
```

## Middleware Examples

### Authentication

```python
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware


class AuthMiddleware(BaseMiddleware):
    def __init__(self, token: str):
        self.token = token

    async def before_request(self, route, config):
        headers = config.get("headers", {})
        headers["Authorization"] = f"Bearer {self.token}"
        config["headers"] = headers
        return config


app = FastHTTP(middleware=[AuthMiddleware(token="your-token")])
```

### Adding Trace ID

```python
import uuid
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware


class TraceMiddleware(BaseMiddleware):
    async def before_request(self, route, config):
        trace_id = str(uuid.uuid4())
        headers = config.get("headers", {})
        headers["X-Trace-ID"] = trace_id
        config["headers"] = headers
        return config


app = FastHTTP(middleware=[TraceMiddleware()])
```

### Logging

```python
import time
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware


class LoggingMiddleware(BaseMiddleware):
    async def before_request(self, route, config):
        print(f"🚀 Sending: {route.method} {route.url}")
        config["_start_time"] = time.time()
        return config

    async def after_response(self, response, route, config):
        start_time = config.get("_start_time", 0)
        duration = time.time() - start_time
        print(f"✅ Response: {route.method} {route.url} - {response.status} ({duration:.2f}s)")
        return response


app = FastHTTP(middleware=[LoggingMiddleware()])
```

### Caching

FastHTTP comes with built-in CacheMiddleware:

```python
from fasthttp import FastHTTP, CacheMiddleware

app = FastHTTP(middleware=[
    CacheMiddleware(ttl=3600, max_size=100)  # TTL in seconds, max cache size
])
```

Caches GET requests in memory.

### Rate Limiting

```python
import time
from collections import defaultdict
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, max_requests: int = 10, window: int = 60):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)

    async def before_request(self, route, config):
        now = time.time()
        host = config.get("headers", {}).get("Host", "default")
        
        # Clean old requests
        self.requests[host] = [
            t for t in self.requests[host] 
            if now - t < self.window
        ]
        
        # Check limit
        if len(self.requests[host]) >= self.max_requests:
            raise Exception(f"Rate limit exceeded: {self.max_requests} requests per {self.window}s")
        
        self.requests[host].append(now)
        return config


app = FastHTTP(middleware=[RateLimitMiddleware(max_requests=10, window=60)])
```

### Response Modification

```python
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware


class ResponseModifierMiddleware(BaseMiddleware):
    async def after_response(self, response, route, config):
        # Add headers to response
        response.headers["X-Custom-Response"] = "value"
        return response


app = FastHTTP(middleware=[ResponseModifierMiddleware()])
```

## Middleware Lifecycle

```
before_request → [Send Request] → after_response
                    or
                 on_error
```

### before_request(route, config)

Called before sending each request. Can modify `config`.

**Parameters:**
- `route` — route information
- `config` — request configuration

**Returns:** modified `config`

### after_response(response, route, config)

Called after receiving a response. Can modify `response`.

**Parameters:**
- `response` — response object
- `route` — route information
- `config` — request configuration

**Returns:** modified `response`

### on_error(error, route, config)

Called when an error occurs.

**Parameters:**
- `error` — exception
- `route` — route information
- `config` — request configuration

**Can:**
- Handle error and return a value
- Re-raise the error

## Comparison with Dependencies

| Feature | Middleware | Dependencies |
|---------|------------|--------------|
| Global application | ✅ Yes | ❌ No |
| Application to specific request | ❌ No | ✅ Yes |
| Response modification | ✅ Yes | ❌ No |
| Error handling | ✅ Yes | ❌ No |
| Complexity | Higher | Lower |

## See Also

- [Dependencies](dependencies.md) — for specific requests
- [Configuration](configuration.md) — settings
- [Quick Start](quick-start.md) — basics

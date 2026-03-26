# Middleware Examples

Practical middleware examples.

## Authentication Middleware

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

## Logging Middleware

```python
import time
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware


class LoggingMiddleware(BaseMiddleware):
    async def before_request(self, route, config):
        print(f"Sending: {route.method} {route.url}")
        config["_start_time"] = time.time()
        return config

    async def after_response(self, response, route, config):
        start_time = config.get("_start_time", 0)
        duration = time.time() - start_time
        print(f"Response: {route.method} {route.url} - {response.status} ({duration:.2f}s)")
        return response


app = FastHTTP(middleware=[LoggingMiddleware()])
```

## Trace ID Middleware

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

## Rate Limiting Middleware

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
            raise Exception(f"Rate limit: {self.max_requests} requests per {self.window}s")
        
        self.requests[host].append(now)
        return config


app = FastHTTP(middleware=[RateLimitMiddleware(max_requests=10, window=60)])
```

## Response Modification Middleware

```python
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware


class ResponseModifierMiddleware(BaseMiddleware):
    async def after_response(self, response, route, config):
        response.headers["X-Custom-Response"] = "value"
        return response


app = FastHTTP(middleware=[ResponseModifierMiddleware()])
```

## Cache Middleware

FastHTTP includes built-in `CacheMiddleware`:

```python
from fasthttp import FastHTTP, CacheMiddleware

app = FastHTTP(middleware=[
    CacheMiddleware(ttl=3600, max_size=100)  # TTL in seconds, max cache size
])
```

Caches GET requests in memory.

# Middleware Examples

## Auth middleware

Adds a Bearer token to every request:

```python
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware


class BearerAuthMiddleware(BaseMiddleware):
    __return_type__ = bool
    __priority__ = 0
    __methods__ = None
    __enabled__ = True

    def __init__(self, token: str) -> None:
        self.token = token

    async def request(self, method, url, kwargs):
        kwargs["headers"] = kwargs.get("headers") or {}
        kwargs["headers"]["Authorization"] = f"Bearer {self.token}"
        return kwargs


app = FastHTTP(middleware=[BearerAuthMiddleware("my-secret-token")])
```

## Logging middleware

Prints every request and response:

```python
from fasthttp.middleware import BaseMiddleware


class LoggingMiddleware(BaseMiddleware):
    __return_type__ = None
    __priority__ = 99
    __methods__ = None
    __enabled__ = True

    async def request(self, method, url, kwargs):
        print(f"→ {method} {url}")
        return kwargs

    async def response(self, response):
        print(f"← {response.status}")
        return response
```

!!! tip
    High `__priority__` — logging runs **last on the way in** (sees final kwargs)
    and **first on the way out** (sees the raw response).

## Timing middleware

Measures request duration:

```python
import time
from contextvars import ContextVar
from fasthttp.middleware import BaseMiddleware


class TimingMiddleware(BaseMiddleware):
    __return_type__ = float
    __priority__ = 0
    __methods__ = None
    __enabled__ = True

    def __init__(self) -> None:
        self._start: ContextVar[float] = ContextVar("timing_start", default=0.0)

    async def request(self, method, url, kwargs):
        self._start.set(time.monotonic())
        return kwargs

    async def response(self, response):
        elapsed = time.monotonic() - self._start.get()
        print(f"Request took {elapsed:.3f}s")
        return response
```

## Trace ID middleware

Adds a unique ID to every request:

```python
import uuid
from fasthttp.middleware import BaseMiddleware


class TraceMiddleware(BaseMiddleware):
    __return_type__ = None
    __priority__ = 0
    __methods__ = None
    __enabled__ = True

    async def request(self, method, url, kwargs):
        kwargs["headers"] = kwargs.get("headers") or {}
        kwargs["headers"]["X-Trace-ID"] = str(uuid.uuid4())
        return kwargs
```

## Method filtering

Run middleware only for specific HTTP methods:

```python
class WriteOpMiddleware(BaseMiddleware):
    __return_type__ = bool
    __priority__ = 1
    __methods__ = ["POST", "PUT", "PATCH", "DELETE"]
    __enabled__ = True

    async def request(self, method, url, kwargs):
        kwargs["headers"] = kwargs.get("headers") or {}
        kwargs["headers"]["X-Write-Op"] = "true"
        return kwargs
```

For `GET`, `HEAD`, and `OPTIONS` this middleware is silently skipped.

## Toggle without removing

Disable middleware at runtime without editing the app:

```python
debug = LoggingMiddleware()

app = FastHTTP(middleware=[debug])

# disable at some point
debug.__enabled__ = False   # not logged

# re-enable
debug.__enabled__ = True    # logged again
```

## Pipe chaining

Combine multiple middleware in one line:

```python
from fasthttp import FastHTTP
from fasthttp.middleware import MiddlewareChain

chain = (
    BearerAuthMiddleware("token")
    | TimingMiddleware()
    | LoggingMiddleware()
)

app = FastHTTP(middleware=chain)
```

Execution order on request: `BearerAuth → Timing → Logging → [HTTP]`  
Execution order on response: `[HTTP] → Logging → Timing → BearerAuth`

## Error tracking middleware

Counts errors and logs context:

```python
from fasthttp.middleware import BaseMiddleware


class ErrorTrackingMiddleware(BaseMiddleware):
    __return_type__ = None
    __priority__ = 0
    __methods__ = None
    __enabled__ = True

    def __init__(self) -> None:
        self.error_count = 0

    async def on_error(self, error, route, config) -> None:
        self.error_count += 1
        print(f"Error #{self.error_count}: {error.__class__.__name__}")
        print(f"  {route.method} {route.url} — {error}")
```

## Caching

FastHTTP includes built-in `CacheMiddleware`:

```python
from fasthttp import FastHTTP, CacheMiddleware

app = FastHTTP(
    middleware=[CacheMiddleware(ttl=3600, max_size=100)]
)
```

- `ttl` — cache time-to-live in seconds
- `max_size` — maximum number of entries (LRU eviction)
- `cache_methods` — list of methods to cache (default `["GET"]`)

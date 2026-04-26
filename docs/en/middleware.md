# Middleware

Middleware lets you intercept and modify every request and response through `FastHTTP` — without changing handler code.

## What middleware can do

- Automatically add authorization headers
- Log all requests and responses
- Add timing and tracing headers
- Retry requests on specific response codes
- Transform response data

## How it works

```
request  →  mw1.request → mw2.request → mw3.request → [HTTP]
response ←  mw1.response ← mw2.response ← mw3.response ← [HTTP]
```

Middleware executes in `__priority__` order on the way in and in **reverse order** on the way out.

## Creating Middleware

Create a class inheriting from `BaseMiddleware`:

```python
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware
from fasthttp.response import Response


class MyMiddleware(BaseMiddleware):
    __return_type__ = None
    __priority__ = 0
    __methods__ = None
    __enabled__ = True

    async def request(self, method, url, kwargs):
        kwargs["headers"] = kwargs.get("headers") or {}
        kwargs["headers"]["X-Custom"] = "value"
        return kwargs

    async def response(self, response):
        return response

    async def on_error(self, error, route, config):
        print(f"Error: {error}")
```

## Attaching to the app

=== "List"

    ```python
    app = FastHTTP(middleware=[AuthMiddleware(), LoggingMiddleware()])
    ```

=== "Pipe"

    ```python
    app = FastHTTP(middleware=AuthMiddleware() | LoggingMiddleware())
    ```

=== "Single"

    ```python
    app = FastHTTP(middleware=MyMiddleware())
    ```

## Examples

### Authentication

```python
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware


class AuthMiddleware(BaseMiddleware):
    __return_type__ = bool
    __priority__ = 0
    __methods__ = None
    __enabled__ = True

    def __init__(self, token: str):
        self.token = token

    async def request(self, method, url, kwargs):
        kwargs["headers"] = kwargs.get("headers") or {}
        kwargs["headers"]["Authorization"] = f"Bearer {self.token}"
        return kwargs


app = FastHTTP(middleware=[AuthMiddleware(token="your-token")])
```

### Adding Trace ID

```python
import uuid
from fasthttp import FastHTTP
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


app = FastHTTP(middleware=[TraceMiddleware()])
```

### Logging

```python
import time
from contextvars import ContextVar
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware


class LoggingMiddleware(BaseMiddleware):
    __return_type__ = None
    __priority__ = 99
    __methods__ = None
    __enabled__ = True

    def __init__(self) -> None:
        self._start: ContextVar[float] = ContextVar("log_start", default=0.0)

    async def request(self, method, url, kwargs):
        print(f"→ {method} {url}")
        self._start.set(time.monotonic())
        return kwargs

    async def response(self, response):
        elapsed = time.monotonic() - self._start.get()
        print(f"← {response.status} ({elapsed:.2f}s)")
        return response


app = FastHTTP(middleware=[LoggingMiddleware()])
```

### Caching

FastHTTP comes with built-in `CacheMiddleware`:

```python
from fasthttp import FastHTTP, CacheMiddleware

app = FastHTTP(
    middleware=[CacheMiddleware(ttl=3600, max_size=100)]
)
```

Caches GET requests in memory with LRU eviction.

### Response modification

```python
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware


class ResponseModifierMiddleware(BaseMiddleware):
    __return_type__ = None
    __priority__ = 0
    __methods__ = None
    __enabled__ = True

    async def response(self, response):
        response.headers["X-Custom-Response"] = "value"
        return response


app = FastHTTP(middleware=[ResponseModifierMiddleware()])
```

## Class attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `__return_type__` | `type \| None` | Type this middleware operates on |
| `__priority__` | `int` | Execution order — **lower runs first** |
| `__methods__` | `list[str] \| None` | HTTP methods to intercept. `None` = all methods |
| `__enabled__` | `bool` | `False` skips without removing from chain |

## Runtime toggle

```python
debug = LoggingMiddleware()
app = FastHTTP(middleware=[debug])

debug.__enabled__ = False   # disable
debug.__enabled__ = True    # re-enable
```

## Comparison with Dependencies

| Feature | Middleware | Dependencies |
|---------|------------|--------------|
| Global application | ✅ Yes | ❌ No |
| Specific request | ❌ No | ✅ Yes |
| Response modification | ✅ Yes | ❌ No |
| Error handling | ✅ Yes | ❌ No |
| Complexity | Higher | Lower |

## See also

- [Creating Middleware](tutorial/middleware/creating.md) — full API, pipe chaining
- [Middleware Examples](tutorial/middleware/examples.md) — ready-made recipes
- [Middleware Reference](reference/middleware.md) — class documentation
- [Dependencies](dependencies.md) — for specific requests

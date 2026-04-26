# Middleware Reference

## BaseMiddleware

Base class for all middleware. Subclass and override `request` and/or `response`.

```python
from fasthttp.middleware import BaseMiddleware

class MyMiddleware(BaseMiddleware):
    __return_type__ = None
    __priority__ = 0
    __methods__ = None
    __enabled__ = True

    async def request(self, method, url, kwargs):
        return kwargs

    async def response(self, response):
        return response

    async def on_error(self, error, route, config):
        pass
```

### Class attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `__return_type__` | `type \| None` | Type this middleware operates on |
| `__priority__` | `int` | Execution order (lower = earlier) |
| `__methods__` | `list[str] \| None` | HTTP methods to apply to. `None` = all |
| `__enabled__` | `bool` | `False` skips without removing from chain |

### Methods

#### `request(method, url, kwargs) → dict`

Called before the request is sent.

| Parameter | Type | Description |
|-----------|------|-------------|
| `method` | `str` | HTTP method (`"GET"`, `"POST"`, etc.) |
| `url` | `str` | Resolved URL |
| `kwargs` | `dict` | Request arguments: `headers`, `params`, `json`, `data`, `timeout` |

**Returns:** modified `kwargs`.

#### `response(response) → Response`

Called after the response is received. Called in **reverse** priority order.

| Parameter | Type | Description |
|-----------|------|-------------|
| `response` | `Response` | Response object |

**Returns:** modified `Response`.

#### `on_error(error, route, config) → None`

Called on request error.

| Parameter | Type | Description |
|-----------|------|-------------|
| `error` | `Exception` | Exception |
| `route` | `Route` | Route information |
| `config` | `dict` | Request configuration |

---

## MiddlewareChain

Ordered chain of middleware instances, created via the `|` operator.

```python
from fasthttp.middleware import MiddlewareChain

chain = AuthMiddleware() | LoggingMiddleware() | TimingMiddleware()
```

Passed directly to `FastHTTP`:

```python
app = FastHTTP(middleware=chain)
```

### Methods

| Method | Description |
|--------|-------------|
| `__or__(other)` | Appends middleware to end of chain |
| `__iter__()` | Iterate over middleware |
| `__len__()` | Number of middleware in chain |
| `__repr__()` | String representation |

---

## MiddlewareManager

Internal manager that drives chain execution. Accepts `list`, `MiddlewareChain`, or `None`.

```python
from fasthttp.middleware import MiddlewareManager

manager = MiddlewareManager([AuthMiddleware(), LoggingMiddleware()])
```

Methods are called automatically by `HTTPClient`.

---

## CacheMiddleware

Built-in middleware for caching responses in memory.

```python
from fasthttp import FastHTTP, CacheMiddleware

app = FastHTTP(
    middleware=[CacheMiddleware(ttl=3600, max_size=100)]
)
```

### Constructor parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ttl` | `int` | `3600` | Cache time-to-live in seconds |
| `max_size` | `int` | `100` | Maximum number of entries (LRU eviction) |
| `cache_methods` | `list[str]` | `["GET"]` | HTTP methods to cache |

### Methods

| Method | Description |
|--------|-------------|
| `clear()` | Clears all cached responses |
| `get_stats()` | Returns cache statistics |

```python
cache = CacheMiddleware(ttl=60)
app = FastHTTP(middleware=[cache])

# later
cache.clear()
print(cache.get_stats())
# {'size': 0, 'max_size': 100, 'ttl': 60, 'methods': ['GET']}
```

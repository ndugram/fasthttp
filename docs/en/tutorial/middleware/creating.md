# Creating Middleware

## BaseMiddleware

All middleware inherits from `BaseMiddleware`:

```python
from fasthttp.middleware import BaseMiddleware

class MyMiddleware(BaseMiddleware):
    __return_type__ = bool
    __priority__ = 0
    __methods__ = None
    __enabled__ = True

    async def request(self, method, url, kwargs):
        # modify kwargs before the request is sent
        return kwargs

    async def response(self, response):
        # inspect or modify the response
        return response

    async def on_error(self, error, route, config):
        # handle the error
        pass
```

## Class attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `__return_type__` | `type \| None` | Type this middleware operates on |
| `__priority__` | `int` | Execution order — **lower runs first** |
| `__methods__` | `list[str] \| None` | HTTP methods to intercept. `None` = all methods |
| `__enabled__` | `bool` | `False` skips middleware without removing it from the chain |

!!! note "No defaults"
    None of these attributes have defaults in `BaseMiddleware`. Define
    only the ones you need.

## `request(method, url, kwargs)`

Called **before** the HTTP request is sent. Receives:

- `method` — HTTP method (`"GET"`, `"POST"`, etc.)
- `url` — resolved URL (scheme already prepended)
- `kwargs` — dict with keys: `params`, `headers`, `json`, `data`, `timeout`

Must return the (possibly modified) `kwargs` dict:

```python
async def request(self, method, url, kwargs):
    kwargs["headers"] = kwargs.get("headers") or {}
    kwargs["headers"]["X-Request-ID"] = "some-id"
    return kwargs
```

!!! warning "headers may be None"
    `kwargs["headers"]` is `None` when no headers were passed.
    Always use `kwargs.get("headers") or {}` before adding keys.

## `response(response)`

Called **after** the HTTP response is received. Receives a `Response` object.
Must return `Response`:

```python
async def response(self, response):
    if response.status >= 400:
        print(f"Error {response.status}")
    return response
```

## `on_error(error, route, config)`

Called on **request error**. Receives:

- `error` — exception
- `route` — route information
- `config` — request configuration

```python
async def on_error(self, error, route, config):
    print(f"Error: {route.method} {route.url} — {error}")
```

## Dunder methods

### `__repr__`

```python
mw = MyMiddleware()
print(mw)   # <MyMiddleware return_type=<class 'bool'>>
```

### `__or__` — pipe chaining

Combine middleware via `|`:

```python
chain = AuthMiddleware() | LoggingMiddleware() | TimingMiddleware()
```

Result is a `MiddlewareChain`, passed directly to `FastHTTP`:

```python
app = FastHTTP(middleware=chain)
```

### `__init_subclass__`

Fires on subclassing `BaseMiddleware`. Override for custom subclass validation:

```python
class StrictMiddleware(BaseMiddleware):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "__priority__"):
            raise TypeError(f"{cls.__name__} must define __priority__")
```

## Attaching to the app

=== "List"

    ```python
    FastHTTP(middleware=[AuthMiddleware(), LoggingMiddleware()])
    ```

=== "Pipe"

    ```python
    FastHTTP(middleware=AuthMiddleware() | LoggingMiddleware())
    ```

=== "Single"

    ```python
    FastHTTP(middleware=AuthMiddleware())
    ```

All three forms are equivalent. Sort order is determined by `__priority__` automatically.

## Runtime toggle

```python
debug = LoggingMiddleware()
app = FastHTTP(middleware=[debug])

# disable without removing from chain
debug.__enabled__ = False

# re-enable
debug.__enabled__ = True
```

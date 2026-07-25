# Function-based Middleware

`@app.middleware("http")` registers a plain async function as middleware, FastAPI-style — no `BaseMiddleware` subclass required.

```python
import time
from fasthttp import FastHTTP, Request
from fasthttp.response import Response

app = FastHTTP()


@app.middleware("http")
async def timing(request: Request, call_next):
    start = time.monotonic()
    response = await call_next(request)
    if response is not None:
        response.headers["X-Elapsed"] = str(time.monotonic() - start)
    return response


@app.get(url="https://httpbin.org/get")
async def get_data(resp: Response) -> dict:
    return resp.json()


app.run()
```

!!! note "Only `"http"` is supported for now"
    WebSocket (`@app.ws`) and GraphQL (`@app.graphql`) requests don't run
    through `HTTPClient`, so they don't go through this decorator yet.
    Calling `app.middleware("ws")` or `app.middleware("graphql")` raises
    `ValueError`. Use [`BaseMiddleware`](creating.md) or
    [event hooks](../../middleware.md#event-hooks) for those in the meantime.

## The `call_next` pattern

Unlike `BaseMiddleware`, which splits `request()`/`response()` into two
separate methods, a function middleware wraps the **entire** call in one
coroutine — including retries, redirects, class-based `BaseMiddleware`,
and the route handler itself:

```
add_trace_id ─┐                                   ┌─ (everything after call_next)
              await call_next(request) ──▶ retries/redirects/BaseMiddleware/handler
              (everything before call_next) ◀──────┘
```

Everything **before** `await call_next(request)` runs before the request is
sent. Everything **after** runs once the response (or `None`, on failure)
comes back — including the route handler's return value already being
processed.

Register several and they nest like a stack — the **first registered is
outermost**:

```python
@app.middleware("http")
async def outer(request: Request, call_next):
    print("outer: before")
    response = await call_next(request)
    print("outer: after")
    return response


@app.middleware("http")
async def inner(request: Request, call_next):
    print("inner: before")
    response = await call_next(request)
    print("inner: after")
    return response
```

Order: `outer: before` → `inner: before` → request sent → `inner: after` → `outer: after`.

## Short-circuiting

Return without calling `call_next(request)` to skip the request entirely
— useful for auth guards or cache short-circuits:

```python
@app.middleware("http")
async def block_blank_host(request: Request, call_next):
    if not request.host:
        return None
    return await call_next(request)
```

## `Request`

`Request` describes the outgoing request *before* it's sent. Unlike an
incoming ASGI request, the body is already fully built — there's nothing
to stream — so only `.headers` is mutable and actually reaches the
request. `.json` / `.content` / `.query_params` are read-only snapshots
for inspection (logging, tracing) — mutating them has no effect, matching
how `BaseMiddleware.request()`'s `kwargs["json"]`/`kwargs["data"]` already
behave.

| Attribute | Type | Description |
|-----------|------|--------------|
| `method` | `str` | HTTP method being sent |
| `url` | `httpx.URL` | Structured URL — `.host`, `.port`, `.scheme`, `.path`, `.params` |
| `host` | `str \| None` | Shortcut for `request.url.host` |
| `headers` | `dict[str, str]` | **Mutable** — changes are sent with the request |
| `query_params` | `dict[str, Any]` | Read-only snapshot of the query params that will be sent |
| `json` | `dict \| None` | Read-only snapshot of the JSON body, if any |
| `content` | `Any` | Read-only snapshot of the raw body/form data, if any |
| `route` | `Route` | The `Route` being executed — `tags`, `response_model`, etc. |
| `app` | `FastHTTP` | The application instance — access app-level config from middleware |
| `state` | `SimpleNamespace` | Per-request scratch space — stash data before `call_next` and read it after |

### Using `.state` to pass data across the call

```python
@app.middleware("http")
async def timing(request: Request, call_next):
    request.state.start = time.monotonic()
    response = await call_next(request)
    elapsed = time.monotonic() - request.state.start
    if response is not None:
        response.headers["X-Elapsed"] = f"{elapsed:.3f}"
    return response
```

## Mixing with class-based middleware

Function middleware (`@app.middleware("http")`) and `BaseMiddleware`
(`FastHTTP(middleware=[...])`) can be used together. Function middleware
always wraps **outside** — it sees the request first and the response
last, with all `BaseMiddleware` instances and the route handler running
in between.

## See also

- [Creating Middleware](creating.md) — class-based `BaseMiddleware` API
- [Middleware Reference](../../reference/middleware.md) — full API reference

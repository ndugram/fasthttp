# Routers

`Router` helps split large FastHTTP applications into smaller reusable groups of routes.

It is useful when you want to:

- keep related requests together
- reuse route groups in multiple apps
- apply a shared `prefix`, `base_url`, `tags`, or `dependencies`
- build nested route trees

## Basic Usage

```python
from fasthttp import FastHTTP, Router
from fasthttp.response import Response

app = FastHTTP()
users = Router(base_url="https://api.example.com", prefix="/users", tags=["users"])


@users.get("/me")
async def get_me(resp: Response) -> dict:
    return resp.json()


@users.get("/list")
async def get_users(resp: Response) -> dict:
    return resp.json()


app.include_router(users)
```

This produces final request URLs:

- `https://api.example.com/users/me`
- `https://api.example.com/users/list`

## Router Parameters

You can configure a router with:

- `base_url` for the host, for example `https://api.example.com`
- `prefix` for a shared path, for example `/v1`
- `tags` inherited by all routes in the router
- `dependencies` inherited by all routes in the router

```python
router = Router(
    base_url="https://api.example.com",
    prefix="/v1",
    tags=["api", "v1"],
)
```

## include_router()

Attach a router to the main app:

```python
app.include_router(router)
```

You can also override values when including it:

```python
app.include_router(
    router,
    prefix="/public",
    tags=["public"],
    base_url="https://gateway.example.com",
)
```

The include-time values are applied before the router's own values.

## Nested Routers

Routers can include other routers.

```python
from fasthttp import FastHTTP, Router
from fasthttp.response import Response

app = FastHTTP()

api = Router(base_url="https://api.example.com", prefix="/v1", tags=["api"])
users = Router(prefix="/users", tags=["users"])


@users.get("/me")
async def get_me(resp: Response) -> dict:
    return resp.json()


api.include_router(users)
app.include_router(api)
```

Final URL:

- `https://api.example.com/v1/users/me`

Final tags:

- `["api", "users"]`

## Routers Across Multiple Files

In real projects, routers are usually placed in separate modules and then assembled in one place with `include_router()`.

Example structure:

```text
src/
  clients/
    integrations/
      __init__.py
      users.py
      orders.py
      payments.py
```

### `users.py`

```python
from fasthttp import Router
from fasthttp.response import Response

router = Router(prefix="/users", tags=["users"])


@router.get("/me")
async def get_me(resp: Response) -> dict:
    return resp.json()


@router.get("/list")
async def get_users(resp: Response) -> dict:
    return resp.json()
```

### `orders.py`

```python
from fasthttp import Router
from fasthttp.response import Response

router = Router(prefix="/orders", tags=["orders"])


@router.get("/")
async def get_orders(resp: Response) -> dict:
    return resp.json()
```

### `__init__.py`

Like in FastAPI or aiogram, you can create a central setup file that collects all routers in one place:

```python
from fasthttp import Router

from src.clients.integrations import orders, payments, users


def setup_integrations_router() -> Router:
    router = Router()

    router.include_router(users.router)
    router.include_router(orders.router)
    router.include_router(payments.router)

    return router
```

### Attach It to the App

```python
from fasthttp import FastHTTP

from src.clients.integrations import setup_integrations_router

app = FastHTTP(base_url="https://api.example.com")
app.include_router(setup_integrations_router())
```

This works especially well when the project grows and you want to collect routers the same way as in FastAPI:

```python
router.include_router(users.router)
router.include_router(orders.router)
router.include_router(payments.router)
```

Or in a smaller aiogram-like style:

```python
from fasthttp import Router

from src.handlers import auth, users


def setup_handlers_router() -> Router:
    router = Router()

    router.include_router(auth.router)
    router.include_router(users.router)

    return router
```

## Relative URLs and base_url

If a route uses a relative path like `"/me"`, FastHTTP needs a `base_url` somewhere in the router tree.

```python
router = Router()


@router.get("/me")
async def get_me(resp: Response) -> dict:
    return resp.json()


app.include_router(router, base_url="https://api.example.com")
```

If no `base_url` is provided, FastHTTP raises `ValueError`.

## base_url in FastHTTP Constructor

You can set `base_url` directly in the `FastHTTP` constructor, and it will be applied to all decorators:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(base_url="https://api.example.com")


@app.get("/users")      # → https://api.example.com/users
async def get_users(resp: Response) -> dict:
    return resp.json()


@app.post("/users")     # → https://api.example.com/users
async def create_user(resp: Response) -> dict:
    return resp.json()


@app.graphql("/graphql")  # → https://api.example.com/graphql
async def query(resp: Response) -> dict:
    return {"query": "{ users { id } }"}
```

This works the same way for all decorators: `get`, `post`, `put`, `patch`, `delete`, and `graphql`.

Absolute URLs are used as-is and ignore `base_url`:

```python
app = FastHTTP(base_url="https://api.example.com")

@app.get("https://other.com/api")  # → https://other.com/api (base_url ignored)
async def other_api(resp: Response) -> dict:
    return resp.json()
```

## When to Use Routers

Use routers when your project has:

- multiple API resources such as users, orders, payments
- different API versions such as `/v1` and `/v2`
- route groups that should share tags or dependencies
- a need to keep large request collections organized

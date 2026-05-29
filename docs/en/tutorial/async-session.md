# AsyncSession

`AsyncSession` is an imperative HTTP client for FastHTTP — similar to `httpx.AsyncClient`. Instead of defining requests with decorators and calling `app.run()`, you call methods directly and get the response back immediately.

## When to Use AsyncSession vs FastHTTP

| | `FastHTTP` | `AsyncSession` |
|---|---|---|
| Style | Declarative (decorators) | Imperative (direct calls) |
| Execution | All at once via `app.run()` | One request at a time |
| Result | Logged | Returned directly |
| Use case | Batch requests, scripts | Dynamic logic, loops, conditions |

Use `AsyncSession` when you need to:
- Make requests inside loops or conditions
- Use the result immediately to decide what to do next
- Build more complex request flows (e.g., login → fetch token → use token)

## Basic Usage

`AsyncSession` works as an async context manager:

```python
import asyncio
from fasthttp import AsyncSession


async def main():
    async with AsyncSession(base_url="https://jsonplaceholder.typicode.com") as session:
        resp = await session.get("/todos/1")
        if resp:
            print(resp.json())


asyncio.run(main())
```

## HTTP Methods

All standard methods are available:

```python
import asyncio
from fasthttp import AsyncSession


async def main():
    async with AsyncSession(base_url="https://jsonplaceholder.typicode.com") as session:
        # GET
        resp = await session.get("/posts/1")

        # GET with query params
        resp = await session.get("/posts", params={"userId": 1})

        # POST with JSON body
        resp = await session.post("/posts", json={"title": "hello", "userId": 1})

        # PUT
        resp = await session.put("/posts/1", json={"id": 1, "title": "updated", "userId": 1})

        # PATCH
        resp = await session.patch("/posts/1", json={"title": "patched"})

        # DELETE
        resp = await session.delete("/posts/1")

        # HEAD
        resp = await session.head("/posts")

        # OPTIONS
        resp = await session.options("/posts")

        # Generic
        resp = await session.request("GET", "/posts/1")


asyncio.run(main())
```

## Constructor Parameters

```python
AsyncSession(
    base_url: str = None,
    headers: dict = None,
    timeout: float = 30.0,
    http2: bool = False,
    proxy: str = None,
    security: bool = True,
    middleware: list = None,
    cookie_jar: CookieJar = None,
    debug: bool = False,
    secret_key: bytes = None,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base_url` | `str` | `None` | Base URL prepended to all relative paths |
| `headers` | `dict` | `None` | Session-level headers sent with every request |
| `timeout` | `float` | `30.0` | Default timeout in seconds |
| `http2` | `bool` | `False` | Enable HTTP/2 |
| `proxy` | `str` | `None` | Proxy server URL |
| `security` | `bool` | `True` | Enable built-in security (SSRF, circuit breaker, etc.) |
| `middleware` | `list` | `None` | Middleware applied to all requests |
| `cookie_jar` | `CookieJar` | `None` | Cookie jar for automatic cookie handling |
| `debug` | `bool` | `False` | Enable debug logging |
| `secret_key` | `bytes` | `None` | Key for HMAC request signing (auto-generated if not set) |

## Session-Level Headers

Headers set on the session are sent with every request:

```python
import asyncio
from fasthttp import AsyncSession


async def main():
    async with AsyncSession(
        base_url="https://api.example.com",
        headers={
            "Authorization": "Bearer my-token",
            "Accept": "application/json",
        },
    ) as session:
        resp = await session.get("/users")   # Authorization header included
        resp = await session.get("/posts")   # Authorization header included


asyncio.run(main())
```

## Per-Request Headers and Timeout

Override headers or timeout for a single request:

```python
import asyncio
from fasthttp import AsyncSession


async def main():
    async with AsyncSession(base_url="https://api.example.com") as session:
        resp = await session.get(
            "/slow-endpoint",
            headers={"X-Custom": "value"},
            timeout=60.0,
        )


asyncio.run(main())
```

Per-request headers are **merged** on top of session headers. Session headers are not replaced.

## Without Context Manager

You can manage the connection pool manually:

```python
import asyncio
from fasthttp import AsyncSession


async def main():
    session = AsyncSession(base_url="https://api.example.com")
    await session.open()

    try:
        resp = await session.get("/users/1")
        if resp:
            print(resp.json())
    finally:
        await session.close()


asyncio.run(main())
```

Always call `close()` when done — it releases the underlying connection pool.

## Working with Responses

`AsyncSession` returns a `Response` object (or `None` on error/4xx+):

```python
import asyncio
from fasthttp import AsyncSession


async def main():
    async with AsyncSession(security=False) as session:
        resp = await session.get("https://jsonplaceholder.typicode.com/posts/1")
        if resp:
            print(resp.status)          # 200
            print(resp.json())          # dict
            print(resp.text)            # raw string
            print(resp.headers)         # dict of response headers


asyncio.run(main())
```

## Dynamic Request Logic

The main strength of `AsyncSession` — using responses to drive subsequent requests:

```python
import asyncio
from fasthttp import AsyncSession


async def main():
    async with AsyncSession(base_url="https://api.example.com") as session:
        # Step 1: login
        auth = await session.post("/auth/login", json={"user": "admin", "pass": "secret"})
        if not auth:
            return

        token = auth.json()["token"]

        # Step 2: use token in next request
        resp = await session.get(
            "/protected/data",
            headers={"Authorization": f"Bearer {token}"},
        )
        if resp:
            print(resp.json())


asyncio.run(main())
```

## With Middleware

All fasthttp middleware works with `AsyncSession`:

```python
import asyncio
from fasthttp import AsyncSession, CacheMiddleware


async def main():
    async with AsyncSession(
        base_url="https://api.example.com",
        middleware=CacheMiddleware(),
        security=False,
    ) as session:
        resp = await session.get("/data")


asyncio.run(main())
```

## With Cookie Jar

```python
import asyncio
from fasthttp import AsyncSession, CookieJar


async def main():
    async with AsyncSession(
        base_url="https://api.example.com",
        cookie_jar=CookieJar(),
    ) as session:
        await session.post("/login", json={"user": "admin"})
        # cookies from Set-Cookie are stored and sent automatically
        resp = await session.get("/dashboard")


asyncio.run(main())
```

## Import

```python
from fasthttp import AsyncSession
# or
from fasthttp.session import AsyncSession
```

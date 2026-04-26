# Middleware

Middleware lets you intercept and modify **every request and response** through `FastHTTP` — without changing handler code.

## What middleware can do

- Automatically add authorization headers
- Log all requests and responses
- Add timing and tracing headers
- Transform response data
- Track errors and metrics

## How it works

```
request  →  mw1.request → mw2.request → mw3.request → [HTTP]
response ←  mw1.response ← mw2.response ← mw3.response ← [HTTP]
```

Middleware executes in `__priority__` order on the way in and in **reverse order** on the way out.

## Quick example

```python
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware
from fasthttp.response import Response


class LoggingMiddleware(BaseMiddleware):
    __return_type__ = None
    __priority__ = 0
    __methods__ = None
    __enabled__ = True

    async def request(self, method, url, kwargs):
        print(f"→ {method} {url}")
        return kwargs

    async def response(self, response):
        print(f"← {response.status}")
        return response


app = FastHTTP(middleware=[LoggingMiddleware()])
```

Output:

```
→ GET https://httpbin.org/get
← 200
```

## Next steps

- [Creating Middleware](creating.md) — BaseMiddleware API, class attributes, pipe chaining
- [Examples](examples.md) — auth, logging, timing, method filtering, toggle

## Comparison with dependencies

| Feature | Middleware | Dependencies |
|---------|------------|--------------|
| Global application | Yes | No |
| Specific request | No | Yes |
| Can modify response | Yes | No |
| Error handling | Yes | No |

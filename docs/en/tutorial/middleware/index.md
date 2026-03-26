# Middleware

Middleware allows adding global logic executed for all requests.

## Overview

- [Creating Middleware](creating.md) - How to create custom middleware
- [Examples](examples.md) - Practical middleware examples

## Quick Example

```python
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware
from fasthttp.response import Response


class MyMiddleware(BaseMiddleware):
    async def before_request(self, route, config):
        # Runs before each request
        config.setdefault("headers", {})["X-Custom"] = "value"
        return config

    async def after_response(self, response, route, config):
        # Runs after each response
        return response


app = FastHTTP(middleware=[MyMiddleware()])
```

## Lifecycle

```
before_request -> [Send Request] -> after_response
                    or
                 on_error
```

## Comparison with Dependencies

| Feature | Middleware | Dependencies |
|---------|------------|--------------|
| Global application | Yes | No |
| Specific request | No | Yes |
| Can modify response | Yes | No |
| Error handling | Yes | No |
| Simpler to use | No | Yes |

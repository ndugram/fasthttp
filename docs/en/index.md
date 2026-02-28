# FastHTTP Client Documentation

Welcome to the FastHTTP Client documentation! This guide will help you get started with our fast and simple HTTP client library.

## Documentation Structure

- [Quick Start](quick-start.md) - Get up and running in 2 minutes
- [CLI](cli.md) - Command-line interface for HTTP requests
- [API Reference](api-reference.md) - Complete API documentation
- [Examples](examples.md) - Real-world usage examples
- [Configuration](configuration.md) - Advanced configuration options
- [Middleware](middleware.md) - Request/response interception
- [Pydantic Validation](pydantic-validation.md) - Type-safe response validation
- [HTTP/2 Support](http2-support.md) - HTTP/2 protocol support

## What is FastHTTP Client?

FastHTTP Client is a modern asynchronous HTTP client library built on top of httpx. It provides:

- **Simple API** - Minimal boilerplate for HTTP requests
- **Beautiful logging** - Detailed request/response logging with timing
- **Type safety** - Full type annotations for better development experience
- **Async support** - High-performance asynchronous operations
- **All HTTP methods** - Support for GET, POST, PUT, PATCH, DELETE
- **HTTP/2 support** - Optional HTTP/2 protocol support
- **Middleware** - Request/response interception and modification
- **Rate limiting** - Multiple strategies for controlling request rate
- **Pydantic validation** - Type-safe response validation with models

## Key Features

### Simple and Intuitive
```python
from fasthttp import FastHTTP

app = FastHTTP()

@app.get(url="https://api.github.com/users/octocat")
async def get_user(resp):
    return resp.json()
```

### Detailed Logging
```
16:09:18.955 │ INFO     │ fasthttp │ ✔ Sending 1 request
16:09:19.519 │ INFO     │ fasthttp │ ✔ ← GET https://api.github.com [200] 458.26ms
```

### Type Safety
```python
from fasthttp.response import Response

@app.get(url="https://api.example.com")
async def handler(resp: Response) -> str:
    return resp.json()
```

## Perfect For

- **API testing** - Quick and easy HTTP client development
- **Web scraping** - Simple HTTP requests with logging
- **Microservices** - Lightweight HTTP client for service communication
- **Prototyping** - Fast development with beautiful output

## Next Steps

Ready to get started? Check out our [Quick Start Guide](quick-start.md) or explore the [API Reference](api-reference.md).

---

*FastHTTP Client - Making HTTP requests fast and beautiful*

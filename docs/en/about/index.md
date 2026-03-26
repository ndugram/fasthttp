# About

Information about FastHTTP.

## What is FastHTTP?

FastHTTP is a lightweight asynchronous HTTP client framework built on top of httpx. It provides a clean decorator-based API for defining HTTP requests and handling responses.

## Features

- Declarative style - Define requests as functions with decorators
- Async support - Parallel request execution with asyncio
- Dependencies - Modify requests before sending
- Tags - Group and filter requests
- Middleware - Global logic for all requests
- Pydantic - Response validation
- HTTP/2 - Modern protocol support
- CLI - Convenient command line interface
- Built-in security - SSRF protection, circuit breaker

## Why FastHTTP?

Traditional HTTP clients require verbose boilerplate code:

```python
# Too much boilerplate
import aiohttp

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.example.com/data") as resp:
            data = await resp.json()
```

FastHTTP simplifies this:

```python
# Clean and simple
from fasthttp import FastHTTP

app = FastHTTP()

@app.get(url="https://api.example.com/data")
async def main(resp):
    return resp.json()
```

## License

MIT License

## GitHub

https://github.com/ndugram/fasthttp

## Documentation

https://fasthttp.ndugram.dev

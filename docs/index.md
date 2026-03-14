<p align="center">
  <img src="logo-repo.png" alt="FastHTTP" width="600">
</p>

# FastHTTP Client

Fast and simple HTTP client library with async support and beautiful logging.

[![PyPI Version](https://img.shields.io/pypi/v/fasthttp-client?style=flat&label=PyPI)](https://pypi.org/project/fasthttp-client/)
[![Python Versions](https://img.shields.io/pypi/pyversions/fasthttp-client?style=flat)](https://pypi.org/project/fasthttp-client/)
[![License](https://img.shields.io/pypi/l/fasthttp-client?style=flat)](https://github.com/ndugram/fasthttp)
[![Downloads](https://img.shields.io/pypi/dm/fasthttp-client?style=flat)](https://pypi.org/project/fasthttp-client/)

---

## Features

| | |
|:---|:---|
| **Declarative Style** | Define requests as functions with decorators |
| **Async Support** | Parallel request execution with asyncio |
| **Dependencies** | Modify requests before sending |
| **Tags** | Group and filter requests |
| **Middleware** | Global logic for all requests |
| **Pydantic** | Response validation |
| **HTTP/2** | Modern protocol support |
| **CLI** | Convenient command line |

---

## Installation

```bash
pip install fasthttp-client
```

For HTTP/2:

```bash
pip install fasthttp-client[http2]
```

---

## Quick Example

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def main(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()
```

!!! tip "Important"
    Handler functions must have a return type annotation (`-> dict`, `-> str`, `-> int`, etc.)

---

## Documentation

### Getting Started

- [Quick Start](en/quick-start.md) - Start here
- [Configuration](en/configuration.md) - App settings
- [CLI](en/cli.md) - Command line

### Advanced Topics

- [Dependencies](en/dependencies.md) - Request modification
- [Middleware](en/middleware.md) - Global logic
- [GraphQL](en/graphql.md) - GraphQL support
- [Pydantic](en/pydantic-validation.md) - Validation
- [HTTP/2](en/http2-support.md) - HTTP/2 support
- [Security](en/security.md) - Built-in protection

### Additional

- [Examples](en/examples.md) - More code examples
- [API Reference](en/api-reference.md) - Complete reference

---

## Why FastHTTP?

### The Problem

```python
# Too much boilerplate code
import aiohttp

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.example.com/data") as resp:
            data = await resp.json()
            # ... processing
```

### FastHTTP Solution

```python
# Clean and simple code
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.get(url="https://api.example.com/data")
async def main(resp: Response) -> dict:
    return resp.json()
```

---

## Comparison

| Feature | FastHTTP | requests | aiohttp | httpx |
|:---|:---:|:---:|:---:|:---:|
| Declarative | Yes | No | No | No |
| Async | Yes | No | Yes | Yes |
| Dependencies | Yes | No | No | No |
| Tags | Yes | No | No | No |
| Middleware | Yes | No | No | No |
| Pydantic | Yes | No | No | No |
| HTTP/2 | Yes | No | No | Yes |
| CLI | Yes | No | No | No |

---

## Language

- [English Documentation](en/index.md)
- [Russian Documentation](ru/index.md)

---

## License

MIT License

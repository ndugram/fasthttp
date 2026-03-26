# FastHTTP

FastHTTP is a lightweight asynchronous HTTP client built on top of httpx. It provides a clean declarative API for defining HTTP requests and handling responses.

## Features

- **Declarative Style** - Define requests as functions with decorators
- **Async Support** - Parallel request execution with asyncio
- **Dependencies** - Modify requests before sending
- **Tags** - Group and filter requests
- **Middleware** - Global logic for all requests
- **Pydantic** - Response validation
- **HTTP/2** - Support for modern protocol
- **CLI** - Convenient command line interface
- **Built-in Security** - SSRF protection, circuit breaker

## Installation

```bash
pip install fasthttp-client
```

For HTTP/2 support:

```bash
pip install fasthttp-client[http2]
```

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

Output:

```
INFO    | fasthttp    | FastHTTP started
INFO    | fasthttp    | Sending 1 requests
INFO    | fasthttp    | GET https://jsonplaceholder.typicode.com/posts/1 200 234.56ms
INFO    | fasthttp    | Done in 0.24s
```

## Why FastHTTP?

Traditional HTTP clients require verbose code:

```python
# Lots of boilerplate code
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

## Documentation

- [Learn](en/learn/index.md) - Fundamental concepts
- [Tutorial](en/tutorial/index.md) - User guide
- [CLI](en/cli/index.md) - Command line interface
- [Reference](en/reference/index.md) - API reference
- [About](en/about/index.md) - About the project

## GitHub

https://github.com/ndugram/fasthttp

## Documentation Site

https://fasthttp.ndugram.dev

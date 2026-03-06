# FastHTTP

Asynchronous HTTP client for Python with a declarative approach, similar to FastAPI.

## Features

- **Declarative style** — define requests as functions with decorators
- **Asynchronous** — parallel request execution with asyncio
- **Dependencies** — modify requests before sending
- **Tags** — grouping and filtering requests
- **Middleware** — global logic for all requests
- **Pydantic** — response validation
- **HTTP/2** — support for modern protocol
- **CLI** — convenient command line

## Installation

```bash
pip install fasthttp-client
```

For HTTP/2:

```bash
pip install fasthttp-client[http2]
```


## Quick Example

```python
from fasthttp import FastHTTP

app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def main(resp):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

## Why FastHTTP?

### The Problem

Usually when working with HTTP requests in Python:

```python
# Lots of boilerplate code
import aiohttp

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.example.com/data") as resp:
            data = await resp.json()
            # ... handling
```

### Solution with FastHTTP

```python
# Clean and clear code
from fasthttp import FastHTTP

app = FastHTTP()

@app.get(url="https://api.example.com/data")
async def main(resp):
    return resp.json()
```

## Documentation

### Basics

- [Quick Start](quick-start.md) — start here
- [Configuration](configuration.md) — application settings
- [CLI](cli.md) — command line

### Advanced Topics

- [Dependencies](dependencies.md) — request modification
- [Middleware](middleware.md) — global logic
- [Pydantic](pydantic-validation.md) — validation
- [HTTP/2](http2-support.md) — HTTP/2 support

### Additional

- [Examples](examples.md) — more code examples
- [API Reference](api-reference.md) — complete reference

## Comparison with Other Libraries

| Library | Style | Async | Dependencies |
|---------|-------|-------|--------------|
| **FastHTTP** | Declarative | ✅ Yes | ✅ Yes |
| requests | Imperative | ❌ No | ❌ No |
| aiohttp | Imperative | ✅ Yes | ❌ No |
| httpx | Imperative | ✅ Yes | ❌ No |

## Usage Examples

### Multiple Parallel Requests

```python
from fasthttp import FastHTTP

app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def get_post(resp):
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/users/1")
async def get_user(resp):
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/comments/1")
async def get_comment(resp):
    return resp.json()


# All three requests execute in parallel!
if __name__ == "__main__":
    app.run()
```

### With Tags

```python
from fasthttp import FastHTTP

app = FastHTTP()


@app.get(url="https://api.example.com/users", tags=["users"])
async def get_users(resp):
    return resp.json()


@app.get(url="https://api.example.com/posts", tags=["posts"])
async def get_posts(resp):
    return resp.json()


# Run only users
app.run(tags=["users"])
```

### With Dependencies

```python
from fasthttp import FastHTTP, Depends

app = FastHTTP()


async def add_auth(route, config):
    config.setdefault("headers", {})["Authorization"] = "Bearer token"
    return config


@app.get(
    url="https://api.example.com/data",
    dependencies=[Depends(add_auth)]
)
async def protected(resp):
    return resp.json()
```

## Community

- GitHub: https://github.com/your-repo/fasthttp
- PyPI: https://pypi.org/project/fasthttp-client/

## License

MIT License

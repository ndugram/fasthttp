# FastHTTP

Modern async HTTP client with beautiful logging.

## Install

```bash
pip install fasthttp-client
```

## Quick Example

```python
from fasthttp import FastHTTP

app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/users/1")
async def main(resp):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

Output:
```
✔ GET https://jsonplaceholder.typicode.com/users/1 [200] 234.56ms
```

## Why FastHTTP?

### Simple API

No boilerplate, no complex setup. Just decorate your async functions:

```python
@app.get(url="https://api.example.com/data")
async def handler(resp):
    return resp.json()
```

### Beautiful Logging

See what happens with each request — status codes, timing, errors:

```
✔ GET https://api.example.com/users [200] 156.32ms
✔ POST https://api.example.com/users [201] 89.12ms
✗ GET https://api.example.com/missing [404]
```

Enable debug mode for full request/response details:

```python
app = FastHTTP(debug=True)
```

### Type Safety

Full type hints for IDE autocompletion and error prevention:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response


@app.get(url="https://api.example.com/users")
async def get_users(resp: Response) -> dict:
    return resp.json()
```

### All HTTP Methods

```python
@app.get(url="https://api.example.com/users")
async def get_users(resp):
    return resp.json()


@app.post(url="https://api.example.com/users", json={"name": "John"})
async def create_user(resp):
    return resp.status


@app.put(url="https://api.example.com/users/1", json={"name": "Jane"})
async def update_user(resp):
    return resp.status


@app.patch(url="https://api.example.com/users/1", json={"age": 25})
async def patch_user(resp):
    return resp.status


@app.delete(url="https://api.example.com/users/1")
async def delete_user(resp):
    return resp.status
```

### Query Parameters

Pass query params easily:

```python
@app.get(url="https://api.example.com/search", params={"q": "fast", "page": 1})
async def search(resp):
    return resp.json()
```

### Concurrent Requests

All registered requests run concurrently:

```python
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


app.run()  # All three requests run in parallel
```

## Features

| Feature | Description |
|---------|-------------|
| **Async** | Built on httpx for high performance |
| **Logging** | Beautiful colored output with timing |
| **Type hints** | Full IDE autocompletion support |
| **Middleware** | Intercept and modify requests/responses |
| **Pydantic** | Validate responses with models |
| **HTTP/2** | Optional HTTP/2 support |

## Use Cases

- **API Testing** — quickly test HTTP endpoints
- **Web Scraping** — simple requests with logging
- **Microservices** — lightweight HTTP client
- **Prototyping** — fast development with pretty output

## Next Steps

- [Quick Start](en/quick-start.md) — get started in 2 minutes
- [CLI](en/cli.md) — command-line usage
- [API Reference](en/api-reference.md) — complete API
- [Middleware](en/middleware.md) — request interception
- [Configuration](en/configuration.md) — options

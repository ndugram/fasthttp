# Quick Start

Install and make your first request in 2 minutes.

## Install

```bash
pip install fasthttp-client
```

## First Request

```python
from fasthttp import FastHTTP

app = FastHTTP()

@app.get(url="https://example.com")
async def main(resp):
    return resp.json()
```

```bash
python main.py
```

Output:
```
16:09:19 │ INFO │ fasthttp │ ✔ ← GET https://example.com [200] 123ms
```

## Configuration

```python
app = FastHTTP(
    debug=True,
    get_request={
        "headers": {"User-Agent": "MyApp/1.0"},
        "timeout": 10,
    },
)
```

## HTTP Methods

```python
@app.get(url="https://api.example.com/users")
async def get_users(resp):
    return resp.json()

@app.post(url="https://api.example.com/users", json={"name": "John"})
async def create_user(resp):
    return resp.status

@app.put(url="https://api.example.com/users/1", json={"name": "Jane"})
async def update_user(resp):
    return resp.json()

@app.patch(url="https://api.example.com/users/1", json={"age": 25})
async def patch_user(resp):
    return resp.status

@app.delete(url="https://api.example.com/users/1")
async def delete_user(resp):
    return resp.status
```

## Response

```python
resp.json()    # Parse JSON
resp.text      # Raw text
resp.status    # Status code (int)
resp.headers   # Response headers
```

## Multiple Requests

2+ requests run in parallel:

```python
app = FastHTTP()

@app.get(url="https://api.example.com/users")
async def get_users(resp):
    return resp.json()

@app.get(url="https://api.example.com/posts")
async def get_posts(resp):
    return resp.json()

app.run()  # Runs both in parallel
```

## Return Values

* `str` — logged as result
* `int` — status code
* `dict/list` — auto-converted to string

```python
@app.get(url="https://example.com")
async def example(resp):
    return resp.status  # 200

@app.get(url="https://example.com")
async def example2(resp):
    return resp.json()  # JSON data
```

## Errors

Auto-caught and logged:

```python
app = FastHTTP(debug=True)

@app.get(url="https://bad-api.com")  # Connection error
@app.get(url="https://httpbin.org/delay/10")  # Timeout
@app.get(url="https://httpbin.org/status/404")  # 404 error
```

Output:
```
ERROR | FastHTTPConnectionError: Connection failed
ERROR | FastHTTPTimeoutError: Request timed out
ERROR | FastHTTPBadStatusError: HTTP 404
```

Manual raise:
```python
from fasthttp.exceptions import FastHTTPBadStatusError

@app.get(url="https://api.example.com/data")
async def get_data(resp):
    if resp.status == 404:
        raise FastHTTPBadStatusError("Not found", url="...", status_code=404)
    return resp.json()
```

## Next

* [API Reference](en/api-reference.md) — full API
* [Configuration](en/configuration.md) — options
* [Middleware](en/middleware.md) — request interception

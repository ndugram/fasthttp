# HTTP/2 Support

FastHTTP supports HTTP/2 for improved performance.

## Installation

For HTTP/2 support, install additional dependencies:

```bash
pip install fasthttp-client[http2]
```

This installs `httpx[http2]` as a dependency.

## Enabling HTTP/2

```python
from fasthttp import FastHTTP

app = FastHTTP(http2=True)
```

## What is HTTP/2?

HTTP/2 is the second version of the HTTP protocol that provides:

- **Multiplexing** — multiple requests over a single connection
- **Header compression** — less data is transmitted
- **Server Push** — server can send data in advance
- **Prioritization** — more important resources load first
- **Single connection** — no need to create a new connection for each request

## HTTP/2 Benefits

### Before HTTP/2

```
Connection 1: GET /page
Connection 2: GET /style.css
Connection 3: GET /script.js
Connection 4: GET /image.png
```

### With HTTP/2

```
Connection 1: GET /page, /style.css, /script.js, /image.png (in parallel)
```

## Usage Example

```python
from fasthttp import FastHTTP

app = FastHTTP(http2=True)


@app.get(url="https://httpbin.org/get")
async def get_data(resp):
    return resp.json()


@app.post(url="https://httpbin.org/post", json={"test": "data"})
async def post_data(resp):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

## Limitations

- Not all servers support HTTP/2
- Requires HTTPS (most browsers)
- Not supported in some proxies

## Checking HTTP/2

```python
from fasthttp import FastHTTP

app = FastHTTP(http2=True)


@app.get(url="https://httpbin.org/get")
async def check_http2(resp):
    # Check if HTTP/2 is being used
    # (depends on server)
    return {
        "status": resp.status,
        "http_version": resp.headers.get("server"),
    }
```

## When to Use HTTP/2

### Yes

- Many parallel requests to the same host
- High network load
- Performance is critical

### No

- Simple single requests
- Server doesn't support HTTP/2
- Need compatibility with older systems

## See Also

- [Configuration](configuration.md) — settings
- [Quick Start](quick-start.md) — basics

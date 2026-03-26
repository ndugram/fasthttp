# HTTP/2 Support

Enable HTTP/2 for improved performance.

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

HTTP/2 is the second version of HTTP protocol with features:

- **Multiplexing** - Multiple requests over single connection
- **Header compression** - Less data transmitted
- **Server Push** - Server sends data in advance
- **Prioritization** - Important resources load first
- **Single connection** - No new connection per request

## Performance Comparison

### Before HTTP/2

```
Connection 1: GET /page
Connection 2: GET /style.css
Connection 3: GET /script.js
Connection 4: GET /image.png
```

### With HTTP/2

```
Connection 1: GET /page, /style.css, /script.js, /image.png (parallel)
```

## Example

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
- Requires HTTPS (most servers)
- Not supported in some proxies

## When to Use

### Yes
- Many parallel requests to same host
- High network load
- Performance is critical

### No
- Simple single requests
- Server doesn't support HTTP/2
- Need compatibility with older systems

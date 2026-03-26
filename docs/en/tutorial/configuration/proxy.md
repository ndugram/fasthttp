# Proxy

Configure proxy server for requests.

## Basic Usage

```python
from fasthttp import FastHTTP

app = FastHTTP(proxy="http://proxy.example.com:8080")
```

## Proxy Types

```python
# HTTP proxy
app = FastHTTP(proxy="http://proxy.example.com:8080")

# HTTPS proxy
app = FastHTTP(proxy="https://proxy.example.com:8080")

# Proxy with authentication
app = FastHTTP(proxy="http://user:password@proxy.example.com:8080")

# SOCKS5 proxy
app = FastHTTP(proxy="socks5://proxy.example.com:1080")
```

## Example

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(
    proxy="http://proxy.example.com:8080",
    get_request={"timeout": 30.0},
)


@app.get(url="https://httpbin.org/get")
async def test_proxy(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()
```

## Environment Variables

You can also configure proxy via environment variables:

```python
import os
from fasthttp import FastHTTP

app = FastHTTP(
    proxy=os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY"),
)
```

## .env File

```bash
HTTP_PROXY=http://proxy.example.com:8080
HTTPS_PROXY=http://proxy.example.com:8080
```

## Use Cases

- Bypassing network restrictions
- Load balancing
- Caching
- Security filtering
- Geographic restrictions

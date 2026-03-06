# Configuration

Detailed guide on configuring FastHTTP.

## Basic Configuration

When creating an application, you can pass global settings:

```python
from fasthttp import FastHTTP

app = FastHTTP(
    debug=False,  # Debug mode
    http2=False,  # Use HTTP/2
    get_request={
        "headers": {"User-Agent": "MyApp/1.0"},
        "timeout": 30.0,
        "allow_redirects": True,
    },
    post_request={
        "headers": {"Content-Type": "application/json"},
        "timeout": 30.0,
        "allow_redirects": True,
    },
)
```

## Configuration Parameters

### Application Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `debug` | `bool` | `False` | Enable verbose logging |
| `http2` | `bool` | `False` | Use HTTP/2 |
| `get_request` | `dict` | `{}` | Default GET settings |
| `post_request` | `dict` | `{}` | Default POST settings |
| `put_request` | `dict` | `{}` | Default PUT settings |
| `patch_request` | `dict` | `{}` | Default PATCH settings |
| `delete_request` | `dict` | `{}` | Default DELETE settings |

### Request Parameters

Each HTTP method can have its own default settings:

```python
app = FastHTTP(
    get_request={
        "headers": {
            "User-Agent": "MyApp/1.0",
            "Accept": "application/json",
        },
        "timeout": 30.0,
        "allow_redirects": True,
    },
    post_request={
        "headers": {
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        "timeout": 60.0,  # POST can take longer
        "allow_redirects": False,
    },
)
```

## Overriding Settings

Settings can be overridden for specific requests:

```python
# Global timeout of 30 seconds
app = FastHTTP(get_request={"timeout": 30.0})


# Override for specific request
@app.get(url="https://api.example.com/fast", timeout=5.0)
async def fast_request(resp):
    return resp.json()


@app.get(url="https://api.example.com/slow", timeout=120.0)
async def slow_request(resp):
    return resp.json()
```

## Headers

### Common Header Types

```python
from fasthttp import FastHTTP

app = FastHTTP()


# Bearer token (most common)
app = FastHTTP(
    get_request={
        "headers": {"Authorization": "Bearer your-token-here"}
    }
)


# API key (alternative method)
app = FastHTTP(
    get_request={
        "headers": {"X-API-Key": "your-api-key"}
    }
)


# Basic Authentication
import base64

app = FastHTTP(
    get_request={
        "headers": {
            "Authorization": f"Basic {base64.b64encode(b'username:password').decode()}"
        }
    }
)


# Custom User-Agent
app = FastHTTP(
    get_request={
        "headers": {"User-Agent": "MyApp/1.0 (https://myapp.com)"}
    }
)
```

### Dynamic Headers

For dynamic headers, use dependencies:

```python
from fasthttp import FastHTTP, Depends

app = FastHTTP()


async def add_auth(route, config):
    import os
    token = os.getenv("API_TOKEN")
    config.setdefault("headers", {})["Authorization"] = f"Bearer {token}"
    return config


@app.get(
    url="https://api.example.com/data",
    dependencies=[Depends(add_auth)]
)
async def handler(resp):
    return resp.json()
```

## Timeout

Timeout is specified in seconds:

```python
# Global timeout
app = FastHTTP(get_request={"timeout": 30.0})


# Local timeout
@app.get(url="https://api.example.com/data", timeout=10.0)
async def handler(resp):
    return resp.json()
```

### Timeout Recommendations

- GET requests: 10-30 seconds
- POST/PUT requests: 30-60 seconds
- File uploads: 120+ seconds

## Logging

### Debug Mode

```python
# Verbose output (all headers, body, time)
app = FastHTTP(debug=True)


# Minimal output (status and time only)
app = FastHTTP(debug=False)
```

When `debug=True`, it outputs:

```
DEBUG   │ fasthttp    │ 🐛 → GET https://api.example.com/data | headers={'User-Agent': 'fasthttp/0.1.0'}
DEBUG   │ fasthttp    │ 🐛 ← 200 | headers={'Content-Type': 'application/json'}
INFO    │ fasthttp    │ ✔ ✔ GET https://api.example.com/data 200 150.23ms
```

When `debug=False`:

```
INFO    │ fasthttp    │ ✔ ✔ GET https://api.example.com/data 200 150.23ms
```

## Environment Variables

Use environment variables for configuration:

```python
import os
from fasthttp import FastHTTP

app = FastHTTP(
    debug=os.getenv("DEBUG", "false").lower() == "true",
    http2=os.getenv("HTTP2", "false").lower() == "true",
    get_request={
        "headers": {
            "Authorization": f"Bearer {os.getenv('API_TOKEN')}",
            "User-Agent": os.getenv("USER_AGENT", "MyApp/1.0"),
        },
        "timeout": float(os.getenv("TIMEOUT", "30.0")),
    },
)
```

### Example .env File

```bash
# .env
DEBUG=true
HTTP2=false
API_TOKEN=your-secret-token
USER_AGENT=MyApp/1.0
TIMEOUT=30.0
```

## HTTP/2

Enable HTTP/2 for improved performance:

```python
app = FastHTTP(http2=True)
```

Requirements:

```bash
pip install fasthttp-client[http2]
```

More details in [HTTP/2](http2-support.md).

## HTTP Method Configuration

You can configure different parameters for different HTTP methods:

```python
app = FastHTTP(
    # Settings for GET
    get_request={
        "headers": {
            "Accept": "application/json",
            "User-Agent": "MyApp/1.0",
        },
        "timeout": 30.0,
    },
    
    # Settings for POST
    post_request={
        "headers": {
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        "timeout": 60.0,
    },
    
    # Settings for PUT
    put_request={
        "headers": {
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        "timeout": 60.0,
    },
    
    # Settings for DELETE
    delete_request={
        "headers": {
            "Accept": "application/json",
        },
        "timeout": 30.0,
    },
)
```

## Configuration Examples

### Minimal Configuration

```python
from fasthttp import FastHTTP

app = FastHTTP()
```

### API Configuration

```python
import os
from fasthttp import FastHTTP

app = FastHTTP(
    debug=os.getenv("DEBUG", "false").lower() == "true",
    get_request={
        "headers": {
            "Authorization": f"Bearer {os.getenv('API_TOKEN')}",
            "User-Agent": "MyApp/1.0",
            "Accept": "application/json",
        },
        "timeout": 30.0,
    },
    post_request={
        "headers": {
            "Authorization": f"Bearer {os.getenv('API_TOKEN')}",
            "Content-Type": "application/json",
            "User-Agent": "MyApp/1.0",
        },
        "timeout": 60.0,
    },
)
```

### Development Configuration

```python
from fasthttp import FastHTTP

app = FastHTTP(
    debug=True,  # Verbose logging
    get_request={
        "headers": {
            "User-Agent": "DevApp/1.0",
        },
        "timeout": 300.0,  # Long timeout for debugging
    },
)
```

## See Also

- [Quick Start](quick-start.md) — basics
- [HTTP/2](http2-support.md) — HTTP/2 support
- [Dependencies](dependencies.md) — request modification
- [CLI](cli.md) — command line

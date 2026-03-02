# Configuration

Customize FastHTTP behavior with various options.

## Basic Setup

```python
from fasthttp import FastHTTP

app = FastHTTP(
    debug=False,    # Enable debug logging
    http2=False,    # Use HTTP/2 protocol
)
```

## Per-Method Configuration

Set defaults for each HTTP method:

```python
app = FastHTTP(
    # Applied to all GET requests
    get_request={
        "headers": {
            "User-Agent": "MyApp/1.0",
            "Accept": "application/json",
        },
        "timeout": 30,
        "allow_redirects": True,
    },

    # Applied to all POST requests
    post_request={
        "headers": {
            "Content-Type": "application/json",
        },
        "timeout": 30,
    },

    # Same for put_request, patch_request, delete_request
)
```

## Request Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `headers` | `dict` | `{}` | Request headers |
| `timeout` | `int` | `30` | Timeout in seconds |
| `allow_redirects` | `bool` | `True` | Follow redirects |

## Headers

### Common Headers

```python
get_request={
    "headers": {
        "User-Agent": "MyApp/1.0",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate",
    },
}
```

### Authentication

**Bearer Token:**

```python
"headers": {
    "Authorization": "Bearer YOUR_JWT_TOKEN",
}
```

**API Key:**

```python
"headers": {
    "X-API-Key": "your-api-key",
}
```

**Basic Auth:**

```python
import base64

credentials = base64.b64encode(b"username:password").decode()
"headers": {
    "Authorization": f"Basic {credentials}",
}
```

## Per-Request Override

Override global config for specific requests:

```python
# This request uses global GET config + custom params
@app.get(url="https://api.example.com/users", params={"page": 1})
async def get_users(resp):
    return resp.json()

# This request uses global GET config + custom headers
@app.get(url="https://api.example.com/private", headers={"X-Secret": "value"})
async def get_private(resp):
    return resp.json()
```

## Environment Variables

Use environment variables for configuration:

```python
import os
from fasthttp import FastHTTP

app = FastHTTP(
    debug=os.getenv("DEBUG", "false").lower() == "true",
    get_request={
        "headers": {
            "Authorization": f"Bearer {os.getenv('API_KEY')}",
        },
        "timeout": int(os.getenv("TIMEOUT", "30")),
    },
)
```

### Environment-Specific Config

```python
import os

ENV = os.getenv("ENV", "dev")

if ENV == "production":
    app = FastHTTP(
        debug=False,
        get_request={"timeout": 10},
    )
elif ENV == "staging":
    app = FastHTTP(
        debug=True,
        get_request={"timeout": 30},
    )
else:  # development
    app = FastHTTP(
        debug=True,
        get_request={"timeout": 60},
    )
```

## Timeout

Set request timeout:

```python
# Global timeout (all GET requests)
app = FastHTTP(get_request={"timeout": 30})

# Per-request timeout
@app.get(url="https://slow-api.com/data", timeout=120)
async def slow_request(resp):
    return resp.json()
```

## Logging

### Default (Info)

Shows status and timing:

```
✔ GET https://api.example.com [200] 234.56ms
✔ POST https://api.example.com/users [201] 89.12ms
```

### Debug Mode

```python
app = FastHTTP(debug=True)
```

Shows:
- Registered routes
- Request headers
- Response headers  
- Response body
- Timing for each step

## HTTP/2

Enable HTTP/2 for better performance:

```python
app = FastHTTP(http2=True)
```

Requires: `pip install fasthttp-client[http2]`

Note: HTTP/2 only works with HTTPS.

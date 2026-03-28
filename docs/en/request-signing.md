# Request Signing

FastHTTP includes built-in automatic request signing using HMAC-SHA256. This feature adds cryptographic signatures to all outgoing HTTP requests to verify their authenticity and detect tampering.

## Overview

When enabled, every request is automatically signed with:
- HTTP method
- Full URL
- Timestamp (UNIX)
- Request body (if present)

The signature is added to request headers:
- `X-Signature` - HMAC-SHA256 hex digest
- `X-Timestamp` - Unix timestamp
- `X-Nonce` - Unique random value per request

## How It Works

### Payload Format

```
METHOD + "\n" + URL + "\n" + TIMESTAMP + "\n" + BODY
```

Example:
```
POST
https://api.example.com/users
1774629340
{"name":"John","email":"john@example.com"}
```

### Signature Generation

1. Serialize body (dict/list → JSON, str → bytes, None → b"")
2. Create payload string
3. Compute HMAC-SHA256 with secret key
4. Add headers to request

## Usage

### Basic Usage

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()

@app.get(url="https://api.example.com/data")
async def handler(resp: Response) -> dict:
    return resp.json()
```

Each request automatically includes:
```
X-Signature: a9a5680104a42814fd6eeec345a7507d41fdcbc71cc636dd2a4dbd3a0566cf79
X-Timestamp: 1774629340
X-Nonce: 2bb9ca6b74f74f051859e39949ac9833
```

### Custom Secret Key

```python
import secrets
from fasthttp import FastHTTP

secret_key = secrets.token_bytes(32)
app = FastHTTP(secret_key=secret_key)
```

If no key is provided, one is automatically generated.

### Disable Signing

```python
app = FastHTTP()
app.security.enable_signing(False)
```

## Security Features

### Replay Attack Protection

- Timestamp validation (max age: 300 seconds)
- Unique nonce per request (16 bytes random)

### Constant-Time Comparison

Uses `hmac.compare_digest()` for signature verification to prevent timing attacks.

### Body Serialization

- `dict`/`list` → JSON via orjson (with sorted keys)
- `str` → UTF-8 bytes
- `bytes` → as-is
- `None` → empty bytes

## Server-Side Verification

To verify incoming signed requests:

```python
import hmac
import time

def verify_signature(
    method: str,
    url: str,
    timestamp: int,
    body: bytes,
    signature: str,
    secret_key: bytes,
    max_age: int = 300
) -> bool:
    if abs(time.time() - timestamp) > max_age:
        return False
    
    payload = f"{method}\n{url}\n{timestamp}\n".encode() + body
    expected = hmac.new(secret_key, payload, digestmod="sha256").hexdigest()
    return hmac.compare_digest(expected, signature)
```

## Configuration

### Access Secret Key

```python
app = FastHTTP()
key = app.security.secret_key
```

### Enable/Disable

```python
app.security.enable_signing(True)   # Enable
app.security.enable_signing(False)  # Disable
```

## Headers Reference

| Header | Type | Description |
|--------|------|-------------|
| `X-Signature` | string | HMAC-SHA256 hex digest |
| `X-Timestamp` | int | Unix timestamp |
| `X-Nonce` | string | 16-byte random hex |

## Example Request

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)

@app.post(
    url="https://api.example.com/users",
    json={"name": "John", "email": "john@example.com"}
)
async def create_user(resp: Response) -> dict:
    return resp.json()

app.run()
```

Debug output shows signed headers:
```
DEBUG | → POST https://api.example.com/users | headers={
    'User-Agent': 'fasthttp/1.0.0',
    'X-Signature': 'e9aebfc284a7f346...',
    'X-Timestamp': '1774629539',
    'X-Nonce': 'da4ec450399cf131...'
}
```

## See Also

- [Security](security.md) - Other security features
- [Configuration](configuration.md) - App configuration

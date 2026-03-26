# SSRF Protection

Server-Side Request Forgery protection.

## What is SSRF?

SSRF (Server-Side Request Forgery) is an attack where an attacker makes the server request internal resources.

## How It Works

FastHTTP automatically blocks requests to:

- `localhost` and variants
- `127.0.0.1`, `0.0.0.0`, `::1`
- Private IP addresses: `10.x.x.x`, `192.168.x.x`, `172.16-31.x.x`
- Link-local addresses: `169.254.x.x`
- Domains: `.local`, `.intranet`, `.internal`

## Example

```python
from fasthttp import FastHTTP

app = FastHTTP()


# This request will be blocked automatically
@app.get(url="http://localhost:8080/admin")
async def blocked_request(resp):
    return resp.json()


app.run()
# Result: SSRF blocked
```

## Disabling

You can disable SSRF protection:

```python
app = FastHTTP(security=False)
```

Not recommended unless you have specific requirements.

## Logging

When a request is blocked, you will see:

```
ERROR | SSRF blocked: SSRF protection blocked request to: http://localhost/test
```

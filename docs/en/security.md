# Security

FastHTTP includes a built-in security system that works under the hood and requires no additional configuration. All checks are performed automatically for every request and response.

## How It Works

The security system is integrated into the library core. For each request:

```
User Request
        ↓
URL Check (SSRF Protection)
        ↓
Header Check
        ↓
Execute Request
        ↓
Response Check
        ↓
Return Result
```

You don't need to configure anything — protection works automatically.

## What's Protected

### SSRF Attack Protection

SSRF (Server-Side Request Forgery) is an attack where an attacker makes the server request internal resources.

FastHTTP automatically blocks requests to:

- `localhost` and its variants
- `127.0.0.1`, `0.0.0.0`, `::1`
- Private IP addresses: `10.x.x.x`, `192.168.x.x`, `172.16-31.x.x`
- Link-local addresses: `169.254.x.x`
- Domains: `.local`, `.intranet`, `.internal`

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

### Secrets Masking in Logs

When debug mode is enabled, FastHTTP automatically hides sensitive data in logs:

- Headers: `Authorization`, `Cookie`, `X-API-Key`
- URL parameters: `api_key`, `token`, `password`

```
# Instead of:
Authorization: Bearer sk-1234567890abcdef

# In logs you will see:
Authorization: *****
```

### Circuit Breaker

If a host stops responding (multiple timeouts or errors), FastHTTP automatically stops sending requests to that host for a while. This protects against:

- Flooding a failed service with requests
- Wasting resources on non-working hosts
- Cascading failures

After a waiting period, FastHTTP periodically checks if the host has recovered.

### Response Size Limit

By default, FastHTTP limits response size to 100 MB. This protects against:

- Giant response attacks
- Memory leaks
- Application hanging

### Header Protection

FastHTTP automatically:

- Sanitizes headers from CRLF characters (HTTP Response Splitting protection)
- Checks incoming headers for suspicious values
- Checks `Set-Cookie` for secure flags

### Timeouts

All requests have built-in timeouts:

- Connection timeout: 10 seconds
- Request timeout: 30 seconds

This prevents application hanging when there are network problems.

### Redirect Protection

FastHTTP limits the number of redirects (default 10) and blocks dangerous redirects:

- To `file://` protocol
- To internal IP addresses
- To `javascript:` or `data:` URLs
- HTTP Downgrade (HTTPS → HTTP)

### Concurrent Request Limit

By default, FastHTTP limits concurrent requests to 100. This protects against accidentally creating too many connections.

## Disabling Protection

All checks are enabled by default. This is the recommended configuration for most cases. If needed, you can disable protection:

```python
from fasthttp import FastHTTP

app = FastHTTP(security=False)
```

Disabling protection is not recommended unless you have good reason.

## Logging Security Events

When a request is blocked, you will see a message in logs:

```
ERROR | SSRF blocked: SSRF protection blocked request to: http://localhost/test
ERROR | Circuit breaker open for: api.example.com
ERROR | Security error: Response too large: 150MB
```

Enable debug mode for more detailed information:

```python
app = FastHTTP(debug=True)
app.run()
```

## Best Practices

1. **Don't disable protection** — built-in mechanisms protect against common attacks
2. **Use HTTPS** — to protect data during transmission
3. **Handle errors** — check return values for None on errors
4. **Monitor logs** — regularly check logs for blocked requests

## Security by Default

The main advantage of the FastHTTP security system is that it works "out of the box". You don't need to configure anything to get protection against:

- SSRF attacks
- Secret leaks in logs
- Overload from non-working hosts
- Too large responses
- Dangerous redirects
- Request hanging

Just use the library — security is already built-in.

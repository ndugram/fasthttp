# Authentication

FastHTTP provides built-in authentication classes that work per route via the `auth` parameter on any decorator.

## Available Auth Classes

| Class | Use case |
|-------|----------|
| `BasicAuth(username, password)` | HTTP Basic — base64-encoded credentials |
| `DigestAuth(username, password)` | HTTP Digest — challenge-response handshake |
| `BearerAuth(token)` | Bearer token — OAuth2, JWT, API keys |

All three are imported from `fasthttp` directly and convert to their httpx equivalents at request time.

## BasicAuth

Sends `Authorization: Basic <base64>` on every request to the route:

```python
from fasthttp import FastHTTP, BasicAuth
from fasthttp.response import Response

app = FastHTTP()


@app.get("https://api.example.com/profile", auth=BasicAuth("alice", "s3cr3t"))
async def get_profile(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()
```

## DigestAuth

Performs the full HTTP Digest challenge-response handshake automatically:

```python
from fasthttp import FastHTTP, DigestAuth
from fasthttp.response import Response

app = FastHTTP()


@app.get("https://api.example.com/data", auth=DigestAuth("alice", "s3cr3t"))
async def get_data(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()
```

## BearerAuth

Sends `Authorization: Bearer <token>` — use for OAuth2 access tokens, JWTs, and static API tokens:

```python
from fasthttp import FastHTTP, BearerAuth
from fasthttp.response import Response

app = FastHTTP()


@app.get("https://api.example.com/users", auth=BearerAuth("my-jwt-token"))
async def get_users(resp: Response) -> list:
    return resp.json()


if __name__ == "__main__":
    app.run()
```

## OAuth2ClientCredentials

Acquires a token from the token endpoint using the **Client Credentials** grant type and automatically refreshes it before expiry:

```python
from fasthttp import FastHTTP
from fasthttp.auth import OAuth2ClientCredentials
from fasthttp.response import Response

app = FastHTTP()

auth = OAuth2ClientCredentials(
    token_url="https://auth.example.com/oauth/token",
    client_id="my-client",
    client_secret="my-secret",
    scopes=["read", "write"],
)


@app.get("https://api.example.com/users", auth=auth)
async def get_users(resp: Response) -> list:
    return resp.json()


if __name__ == "__main__":
    app.run()
```

The token is fetched lazily on the first request and cached. FastHTTP automatically requests a new token 60 seconds before the current one expires, based on the `expires_in` field in the token response.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `token_url` | Yes | OAuth2 token endpoint URL |
| `client_id` | Yes | Client identifier |
| `client_secret` | Yes | Client secret |
| `scopes` | No | List of scope strings to request |
| `extra` | No | Additional key-value pairs sent in the token request body |

## Auth on Routers

The `auth` parameter works on all `Router` decorators:

```python
from fasthttp import FastHTTP, Router, BearerAuth
from fasthttp.response import Response

TOKEN = "my-service-token"

app = FastHTTP()
payments = Router(base_url="https://payments.example.com", prefix="/v1")


@payments.post("/charge", auth=BearerAuth(TOKEN))
async def charge(resp: Response) -> dict:
    return resp.json()


@payments.get("/history", auth=BearerAuth(TOKEN))
async def history(resp: Response) -> list:
    return resp.json()


app.include_router(payments)

if __name__ == "__main__":
    app.run()
```

## Mixing Auth Types

Different routes can use different auth classes:

```python
from fasthttp import FastHTTP, BasicAuth, BearerAuth
from fasthttp.response import Response

app = FastHTTP()


@app.get("https://legacy.example.com/api", auth=BasicAuth("admin", "pass"))
async def legacy(resp: Response) -> dict:
    return resp.json()


@app.get("https://modern.example.com/api", auth=BearerAuth("jwt-token"))
async def modern(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()
```

## No Auth

Omit `auth` (default `None`) to send no authentication headers:

```python
@app.get("https://api.example.com/public")
async def public(resp: Response) -> dict:
    return resp.json()
```

## Combining with raise_for_status

Auth and `raise_for_status` can be set together on the same route:

```python
from fasthttp import FastHTTP, BearerAuth
from fasthttp.exceptions import FastHTTPBadStatusError
from fasthttp.response import Response

app = FastHTTP()


@app.get(
    "https://api.example.com/secure",
    auth=BearerAuth("my-token"),
    raise_for_status=True,
)
async def secure(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    try:
        app.run()
    except FastHTTPBadStatusError as e:
        print(f"HTTP {e.status_code} on {e.url}")
```

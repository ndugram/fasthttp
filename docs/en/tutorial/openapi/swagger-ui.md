# Swagger UI

Interactive API documentation and testing.

## Quick Start

Run your application with `web_run()`:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.get("https://httpbin.org/get")
async def get_data(resp: Response) -> dict:
    return resp.json()


app.web_run()
```

After running, open in browser:

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **OpenAPI Schema**: `http://127.0.0.1:8000/openapi.json`

## Available Endpoints

| Endpoint | Description |
|----------|-------------|
| `/docs` | Swagger UI interface |
| `/openapi.json` | OpenAPI schema in JSON |
| `/request` | Proxy for executing requests |

## Using Swagger UI

### Viewing Documentation

All HTTP requests are automatically displayed with:

- HTTP method (GET, POST, PUT, DELETE)
- URL address
- Description from docstring
- Request parameters
- Pydantic response models

### Testing Requests

1. Find the desired endpoint in the list
2. Click to expand
3. Click **"Execute"** button
4. View response in **Response** section

## Custom Host and Port

```python
app.web_run(host="0.0.0.0", port=8080)
```

## Custom Docs Base URL

```python
app.web_run(base_url="/api")
```

Now the docs will be available at `http://127.0.0.1:8000/api/docs`.

## Customizing API Info

Pass `title`, `version`, and `description` to `FastHTTP` to control what Swagger UI shows in the header:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(
    title="Payments API",
    version="3.1.0",
    description="""
## Payments API

Charge cards, issue refunds, and query transaction history.

Markdown is **supported**.
""",
)


@app.get("https://api.example.com/transactions")
async def list_transactions(resp: Response) -> list:
    """List recent transactions."""
    return resp.json()


app.web_run()
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `title` | `"FastHTTP API"` | API name shown in Swagger UI header |
| `version` | `"1.0.0"` | Version string next to the title |
| `description` | `""` | Markdown description below the title |

## Security Schemes in Swagger UI

When routes use `auth=`, FastHTTP automatically adds the corresponding security scheme to `components/securitySchemes` and attaches a lock icon to protected operations in Swagger UI.

```python
from fasthttp import FastHTTP, BearerAuth, BasicAuth
from fasthttp.response import Response

app = FastHTTP(title="Secure API", version="1.0.0")


@app.get(
    "https://api.example.com/profile",
    auth=BearerAuth(token="my-token"),
    tags=["users"],
)
async def get_profile(resp: Response) -> dict:
    """Protected with Bearer token."""
    return resp.json()


@app.get(
    "https://legacy.example.com/data",
    auth=BasicAuth(username="admin", password="pass"),
    tags=["legacy"],
)
async def get_legacy_data(resp: Response) -> dict:
    """Protected with Basic auth."""
    return resp.json()


@app.get("https://api.example.com/status", tags=["public"])
async def status(resp: Response) -> dict:
    """Public — no lock icon."""
    return resp.json()


app.web_run()
```

FastHTTP emits the following scheme entries automatically:

| Auth class | Scheme name | OpenAPI type |
|------------|-------------|--------------|
| `BearerAuth` | `bearerAuth` | `http / bearer / JWT` |
| `BasicAuth` | `basicAuth` | `http / basic` |
| `DigestAuth` | `digestAuth` | `http / digest` |
| `OAuth2ClientCredentials` | `oauth2ClientCredentials` | `oauth2 / clientCredentials` |

Schemes are only added to the schema when at least one route uses the corresponding `auth=` class.

## With Tags

```python
@app.get("https://api.example.com/data", tags=["users"])
async def get_data(resp: Response) -> dict:
    return resp.json()
```

## Example

```python
from fasthttp import FastHTTP
from fasthttp.response import Response
from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    email: str


app = FastHTTP()


@app.get("https://jsonplaceholder.typicode.com/users/1", response_model=User)
async def get_user(resp: Response) -> dict:
    return resp.json()


@app.post("https://jsonplaceholder.typicode.com/users")
async def create_user(resp: Response) -> dict:
    return resp.json()


# Run with Swagger UI
app.web_run()
```

Now open `http://127.0.0.1:8000/docs` or your prefixed docs URL such as `http://127.0.0.1:8000/api/docs`.

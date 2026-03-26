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

Now open `http://127.0.0.1:8000/docs` to test your requests.

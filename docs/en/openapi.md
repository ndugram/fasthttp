# OpenAPI and Swagger UI

FastHTTP includes built-in support for OpenAPI and Swagger UI for convenient testing and documenting your HTTP requests.

## What is OpenAPI?

OpenAPI (formerly known as Swagger) is a standard for describing REST APIs. It allows you to:

- Automatically generate documentation
- Test APIs through a convenient interface
- Generate client libraries
- Share documentation with your team

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

After running, open in your browser:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **OpenAPI Schema**: `http://127.0.0.1:8000/openapi.json`

## Available Endpoints

| Endpoint | Description |
|----------|-------------|
| `/docs` | Swagger UI interface |
| `/openapi.json` | OpenAPI schema in JSON format |
| `/request` | Proxy for executing requests |

## Using Swagger UI

### Viewing Documentation

All your HTTP requests are automatically displayed in Swagger UI with:
- HTTP method (GET, POST, PUT, DELETE)
- URL address
- Description from docstring
- Request parameters
- Pydantic response models

### Testing Requests

1. Find the desired endpoint in the list
2. Click on it to expand
3. Click the **"Execute"** button
4. View the response in the **Response** section

Swagger automatically redirects the request through the internal proxy to the original URL.

## Examples

### Simple GET Request

```python
@app.get("https://jsonplaceholder.typicode.com/users/1")
async def get_user(resp: Response) -> dict:
    return resp.json()
```

### POST with JSON Body

```python
@app.post("https://jsonplaceholder.typicode.com/users")
async def create_user(resp: Response) -> dict:
    return resp.json()
```

### With Pydantic Model

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

@app.get("https://jsonplaceholder.typicode.com/users/1", response_model=User)
async def get_user(resp: Response) -> dict:
    return resp.json()
```

## Configuration

### Custom Host and Port

```python
app.web_run(host="0.0.0.0", port=8080)
```

### With Tags

```python
@app.get("https://api.example.com/data", tags=["users"])
async def get_data(resp: Response) -> dict:
    return resp.json()
```

## Screenshots

### Swagger UI Home

![Swagger UI Home](../photo/swagger_ui_home.png)

### Execute Request

![Swagger UI Execute](../photo/swagger_ui_check_execute.png)

### View Response

![Swagger UI Response](../photo/swagger_ui_check_web.png)

### 404 Page

![404 Not Found](../photo/404_not_found.png)

## See Also

- [Quick Start](en/quick-start.md)
- [Pydantic Validation](en/pydantic-validation.md)
- [Examples](en/examples.md)

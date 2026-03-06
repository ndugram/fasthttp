# Quick Start

Installation and your first request in less than 2 minutes.

## Installation

Install FastHTTP with pip:

```bash
pip install fasthttp-client
```

For HTTP/2 support, install with additional dependencies:

```bash
pip install fasthttp-client[http2]
```

## Your First Request

Create a file `example.py`:

```python
from fasthttp import FastHTTP

app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def main(resp):
    """Gets post and returns JSON."""
    return resp.json()


if __name__ == "__main__":
    app.run()
```

Run it:

```bash
python example.py
```

Output:

```
INFO    │ fasthttp    │ ✔ FastHTTP started
INFO    │ fasthttp    │ ✔ Sending 1 requests
INFO    │ fasthttp    │ ✔ ✔ GET https://jsonplaceholder.typicode.com/posts/1 200 234.56ms
INFO    │ fasthttp    │ ✔ Done in 0.24s
```

## More About the Application

### What Does FastHTTP Do?

FastHTTP is an asynchronous HTTP client, similar to FastAPI, but for outgoing requests. It allows you to:

- Define HTTP requests as functions with decorators
- Execute multiple requests in parallel
- Add dependencies for request modification
- Use tags for filtering and grouping requests
- Automatically handle errors and logging

### Application Structure

```python
from fasthttp import FastHTTP

# Create application
app = FastHTTP(debug=True)  # debug=True enables verbose logging


# Define request using decorator
@app.get(url="https://api.example.com/data")
async def my_request(resp):
    # resp — response object
    return resp.json()


# Run it
if __name__ == "__main__":
    app.run()
```

## HTTP Methods

FastHTTP supports all main HTTP methods:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


# GET — retrieve data
@app.get(url="https://api.example.com/users")
async def get_users(resp: Response):
    """Get list of users."""
    return resp.json()


# POST — create new data
@app.post(url="https://api.example.com/users", json={"name": "John", "email": "john@example.com"})
async def create_user(resp: Response):
    """Create new user."""
    return resp.json()


# PUT — full data update
@app.put(url="https://api.example.com/users/1", json={"name": "Jane", "email": "jane@example.com"})
async def update_user(resp: Response):
    """Update user completely."""
    return resp.json()


# PATCH — partial data update
@app.patch(url="https://api.example.com/users/1", json={"age": 25})
async def patch_user(resp: Response):
    """Partially update user."""
    return resp.json()


# DELETE — delete data
@app.delete(url="https://api.example.com/users/1")
async def delete_user(resp: Response):
    """Delete user."""
    return resp.status
```

## Request Parameters

### Query Parameters

Use the `params` parameter to add query parameters:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.get(
    url="https://api.example.com/search",
    params={
        "q": "fasthttp",
        "page": 1,
        "limit": 10,
    }
)
async def search(resp: Response):
    """Search with pagination."""
    return resp.json()

# Actual URL: https://api.example.com/search?q=fasthttp&page=1&limit=10
```

### JSON Body

Use the `json` parameter to send JSON:

```python
@app.post(
    url="https://api.example.com/users",
    json={
        "name": "John",
        "email": "john@example.com",
        "age": 25,
    }
)
async def create_user(resp: Response):
    return resp.json()
```

### Raw Data

Use the `data` parameter to send raw data:

```python
@app.post(
    url="https://api.example.com/upload",
    data=b"raw bytes data",
)
async def upload(resp: Response):
    return resp.json()
```

### Headers

Add headers using the `get_request` parameter:

```python
# Global headers for all requests
app = FastHTTP(
    get_request={
        "headers": {
            "Authorization": "Bearer my-secret-token",
            "User-Agent": "MyApp/1.0",
            "Accept": "application/json",
        },
    },
)
```

Or locally for a specific request:

```python
@app.get(
    url="https://api.example.com/data",
    get_request={
        "headers": {
            "X-Custom-Header": "value",
        }
    }
)
async def with_headers(resp: Response):
    return resp.json()
```

## Debug Mode

Enable debug mode to see detailed information:

```python
app = FastHTTP(debug=True)
```

When `debug=True` you will see:
- Request and response headers
- Request and response body
- Execution time of each request
- Full URL with parameters

When `debug=False` (default):
- Only status and execution time

```python
app = FastHTTP(debug=False)  # Brief output
```

## Error Handling

FastHTTP automatically handles errors and logs them:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)


@app.get(url="https://httpbin.org/status/404")
async def handle_error(resp: Response):
    """Handles 404 error."""
    return f"Status: {resp.status}"


@app.get(url="https://httpbin.org/status/500")
async def handle_server_error(resp: Response):
    """Handles 500 error."""
    return f"Status: {resp.status}"
```

### Accessing Status and Response Body

```python
@app.get(url="https://api.example.com/data")
async def handle_response(resp: Response):
    # Status code (200, 404, 500, etc.)
    status = resp.status
    
    # JSON body
    data = resp.json()
    
    # Text response
    text = resp.text
    
    # Response headers
    headers = resp.headers
    
    return {"status": status, "data": data}
```

## Parallel Execution

All requests are executed in parallel using asyncio:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def get_post(resp: Response):
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/users/1")
async def get_user(resp: Response):
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/comments/1")
async def get_comment(resp: Response):
    return resp.json()


if __name__ == "__main__":
    # All three requests execute in parallel
    app.run()
```

Output:

```
INFO    │ fasthttp    │ ✔ FastHTTP started
INFO    │ fasthttp    │ ✔ Sending 3 requests
INFO    │ fasthttp    │ ✔ ✔ GET https://jsonplaceholder.typicode.com/posts/1 200 150ms
INFO    │ fasthttp    │ ✔ ✔ GET https://jsonplaceholder.typicode.com/users/1 200 120ms
INFO    │ fasthttp    │ ✔ ✔ GET https://jsonplaceholder.typicode.com/comments/1 200 110ms
INFO    │ fasthttp    │ ✔ Done in 0.15s  # All requests in parallel!
```

## Return Values

Handler can return different types of data:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


# Return dict — automatically converted to JSON
@app.get(url="https://api.example.com/data")
async def return_dict(resp: Response):
    return {"message": "Hello", "status": resp.status}


# Return list
@app.get(url="https://api.example.com/items")
async def return_list(resp: Response):
    return [1, 2, 3, 4, 5]


# Return string
@app.get(url="https://api.example.com/text")
async def return_string(resp: Response):
    return "Hello, World!"


# Return number (status code)
@app.get(url="https://api.example.com/status")
async def return_number(resp: Response):
    return resp.status


# Return Response object
@app.get(url="https://api.example.com/data")
async def return_response(resp: Response):
    return resp  # Returns the entire response object
```

## Tags

Tags allow grouping and filtering requests:

```python
from fasthttp import FastHTTP

app = FastHTTP()


@app.get(url="https://api.example.com/users", tags=["users"])
async def get_users(resp):
    return resp.json()


@app.post(url="https://api.example.com/users", tags=["users"])
async def create_user(resp):
    return resp.json()


@app.get(url="https://api.example.com/posts", tags=["posts"])
async def get_posts(resp):
    return resp.json()


# Run only users
app.run(tags=["users"])
```

## Dependencies

Dependencies allow modifying requests before sending:

```python
from fasthttp import FastHTTP, Depends
from fasthttp.response import Response

app = FastHTTP()


async def add_auth(route, config):
    """Adds authorization token."""
    config.setdefault("headers", {})["Authorization"] = "Bearer my-token"
    return config


@app.get(
    url="https://api.example.com/protected",
    dependencies=[Depends(add_auth)]
)
async def protected_request(resp: Response):
    return resp.json()
```

More details in [Dependencies](dependencies.md).

## Next Steps

Now you know the basics. Continue learning:

- [Configuration](configuration.md) — more about settings
- [Dependencies](dependencies.md) — request modification
- [Middleware](middleware.md) — global logic
- [CLI](cli.md) — command line
- [API Reference](api-reference.md) — complete reference

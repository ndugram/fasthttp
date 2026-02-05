# Quick Start Guide

Get up and running with FastHTTP Client in under 2 minutes!

## Installation

```bash
pip install fasthttp
```

## Your First Request

Create a file `example.py`:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

# Create the app
app = FastHTTP()

# Register a GET request
@app.get(url="https://httpbin.org/get")
async def get_data(resp: Response) -> str:
    return resp.json()  # Returns JSON data

# Run all requests
if __name__ == "__main__":
    app.run()
```

Run it:
```bash
python example.py
```

**Output:**
```
16:09:18.955 │ INFO     │ fasthttp │ ✔ FastHTTP started
16:09:18.955 │ INFO     │ fasthttp │ ✔ Sending 1 requests
16:09:19.519 │ INFO     │ fasthttp │ ✔ ← GET https://httpbin.org/get [200] 458.26ms
16:09:19.520 │ INFO     │ fasthttp │ ✔ ✔️ GET     https://httpbin.org/get    200 458.26ms
16:09:19.520 │ DEBUG    │ fasthttp │ ↳ {"args": {}, "headers": {"Accept": "*/*", ...}, "url": "https://httpbin.org/get"}
16:09:20.037 │ INFO     │ fasthttp │ ✔ Done in 1.08s
```

## Basic Configuration

### Add Custom Headers
```python
app = FastHTTP(
    get_request={
        "headers": {
            "User-Agent": "MyApp/1.0",
            "Authorization": "Bearer your-token",
        },
        "timeout": 10,
    },
)
```

### Enable Debug Mode
```python
app = FastHTTP(debug=True)  # Shows detailed logging
```

## HTTP Methods

### GET Request
```python
@app.get(url="https://api.example.com/users")
async def get_users(resp: Response):
    return resp.json()
```

### POST Request with JSON
```python
@app.post(url="https://api.example.com/users", json={"name": "John", "age": 30})
async def create_user(resp: Response):
    return f"Created user with status: {resp.status}"
```

### POST with Form Data
```python
@app.post(url="https://api.example.com/upload", data={"key": "value"})
async def upload_data(resp: Response):
    return resp.text
```

### PUT/PATCH Requests
```python
@app.put(url="https://api.example.com/users/1", json={"name": "Jane"})
async def update_user(resp: Response):
    return resp.json()

@app.patch(url="https://api.example.com/users/1", json={"age": 25})
async def patch_user(resp: Response):
    return resp.status
```

### DELETE Request
```python
@app.delete(url="https://api.example.com/users/1")
async def delete_user(resp: Response):
    return f"Delete status: {resp.status}"
```

## Response Handling

### JSON Response
```python
@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def get_post(resp: Response):
    data = resp.json()
    return f"Post title: {data['title']}"
```

### Text Response
```python
@app.get(url="https://httpbin.org/html")
async def get_html(resp: Response):
    return resp.text[:100]  # First 100 characters
```

### Status Code
```python
@app.get(url="https://httpbin.org/status/404")
async def check_status(resp: Response):
    return f"Status: {resp.status}, Headers: {dict(resp.headers)}"
```

## Automatic Error Handling

FastHTTP automatically catches and logs all HTTP errors for you:

- **Connection errors** - when server is unreachable
- **Timeout errors** - when request takes too long
- **HTTP status errors** - when server returns 4xx/5xx codes

```python
from fasthttp import FastHTTP
from fasthttp.exceptions import FastHTTPConnectionError, FastHTTPTimeoutError, FastHTTPBadStatusError

app = FastHTTP(debug=True)

# These will automatically log errors:
@app.get(url="https://nonexistent-domain.com/api")  # Connection error
@app.get(url="https://httpbin.org/delay/10")        # Timeout error  
@app.get(url="https://httpbin.org/status/404")       # HTTP 404 error

if __name__ == "__main__":
    app.run()
```

**Example output with errors:**
```
ERROR | fasthttp.exceptions | ✖ FastHTTPConnectionError: Connection failed | URL: https://nonexistent-domain.com/api | Method: GET
ERROR | fasthttp.exceptions | ✖ FastHTTPTimeoutError: Request timed out | URL: https://httpbin.org/delay/10 | Details: timeout=10
ERROR | fasthttp.exceptions | ✖ FastHTTPBadStatusError: HTTP 404 | URL: https://httpbin.org/status/404 | Status: 404
```

```python
@app.get(url="https://api.example.com/data")
async def get_data(resp: Response):
    if resp.status == 404:
        raise FastHTTPBadStatusError("Data not found", url="https://api.example.com/data", status_code=404)
    return resp.json()
```

## Multiple Requests

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()

# Multiple GET requests
@app.get(url="https://httpbin.org/get")
async def get_data(resp: Response):
    return resp.json()

@app.get(url="https://jsonplaceholder.typicode.com/users/1")
async def get_user(resp: Response):
    return resp.json()

# POST request
@app.post(url="https://httpbin.org/post", json={"test": "data"})
async def post_data(resp: Response):
    return resp.json()

if __name__ == "__main__":
    app.run()
```

## Advanced Examples

### GitHub API Example
```python
app = FastHTTP(
    get_request={
        "headers": {
            "Authorization": "Bearer YOUR_GITHUB_TOKEN",
            "User-Agent": "FastHTTP-App",
        },
    },
)

@app.get(url="https://api.github.com/user")
async def get_github_user(resp: Response):
    user_data = resp.json()
    return f"Hello, {user_data['name']}! You have {user_data['public_repos']} public repos."

@app.get(url="https://api.github.com/repos/microsoft/vscode")
async def get_vscode_stats(resp: Response):
    repo_data = resp.json()
    return f"VS Code has {repo_data['stargazers_count']} stars!"
```

## Return Values

Your handler function can return:

- **str** - Will be logged as result
- **int** - Status code (recommended)
- **dict/list** - JSON data (will be auto-converted to string for logging)
- **Response object** - Full response object

```python
# All of these work:
@app.get(url="https://example.com")
async def example1(resp: Response):
    return resp.status  # Returns 200

@app.get(url="https://example.com")
async def example2(resp: Response):
    return resp.json()  # Returns JSON data

@app.get(url="https://example.com")
async def example3(resp: Response):
    return f"Status: {resp.status}"  # Returns string
```

## Next Steps

- Read the [API Reference](api-reference.md) for detailed documentation
- Check out [Examples](examples.md) for more use cases
- Learn about [Configuration](configuration.md) options

**Happy coding!**

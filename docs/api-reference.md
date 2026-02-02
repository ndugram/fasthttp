# API Reference

Complete reference for all FastHTTP Client classes, methods, and options.

## 📚 Table of Contents

- [FastHTTP Class](#fasthttp-class)
- [Response Class](#response-class)
- [Route Class](#route-class)
- [Configuration Options](#configuration-options)

## 🚀 FastHTTP Class

The main class for creating and managing HTTP requests.

### Constructor

```python
FastHTTP(
    debug: bool = False,
    get_request: dict | None = None,
    post_request: dict | None = None, 
    put_request: dict | None = None,
    patch_request: dict | None = None,
    delete_request: dict | None = None,
) -> FastHTTP
```

#### Parameters

- `debug` (bool): Enable detailed logging (default: `False`)
- `get_request` (dict): Default configuration for GET requests
- `post_request` (dict): Default configuration for POST requests  
- `put_request` (dict): Default configuration for PUT requests
- `patch_request` (dict): Default configuration for PATCH requests
- `delete_request` (dict): Default configuration for DELETE requests

#### Example

```python
from fasthttp import FastHTTP

app = FastHTTP(
    debug=True,
    get_request={
        "headers": {"User-Agent": "MyApp/1.0"},
        "timeout": 10,
    },
    post_request={
        "headers": {"Content-Type": "application/json"},
        "timeout": 30,
    },
)
```

### Methods

#### `.get()`

Register a GET request.

```python
def get(*, url: str, params: dict | None = None) -> Callable
```

**Parameters:**
- `url` (str): Target URL
- `params` (dict): Query parameters (optional)

**Example:**
```python
@app.get(url="https://api.example.com/users", params={"page": 1})
async def get_users(resp: Response):
    return resp.json()
```

#### `.post()`

Register a POST request.

```python
def post(*, url: str, json: dict | None = None, data: dict | None = None, params: dict | None = None) -> Callable
```

**Parameters:**
- `url` (str): Target URL
- `json` (dict): JSON data to send (optional)
- `data` (dict): Form data to send (optional)
- `params` (dict): Query parameters (optional)

**Example:**
```python
@app.post(url="https://api.example.com/users", json={"name": "John"})
async def create_user(resp: Response):
    return resp.status
```

#### `.put()`

Register a PUT request.

```python
def put(*, url: str, json: dict | None = None, data: dict | None = None, params: dict | None = None) -> Callable
```

**Parameters:** Same as `.post()`

**Example:**
```python
@app.put(url="https://api.example.com/users/1", json={"name": "Jane"})
async def update_user(resp: Response):
    return resp.status
```

#### `.patch()`

Register a PATCH request.

```python
def patch(*, url: str, json: dict | None = None, data: dict | None = None, params: dict | None = None) -> Callable
```

**Parameters:** Same as `.post()`

**Example:**
```python
@app.patch(url="https://api.example.com/users/1", json={"age": 25})
async def patch_user(resp: Response):
    return resp.status
```

#### `.delete()`

Register a DELETE request.

```python
def delete(*, url: str, json: dict | None = None, data: dict | None = None, params: dict | None = None) -> Callable
```

**Parameters:** Same as `.post()`

**Example:**
```python
@app.delete(url="https://api.example.com/users/1")
async def delete_user(resp: Response):
    return resp.status
```

#### `.run()`

Execute all registered requests.

```python
def run() -> None
```

**Example:**
```python
if __name__ == "__main__":
    app.run()
```

## 📄 Response Class

Represents an HTTP response with convenient access methods.

### Attributes

- `status` (int): HTTP status code
- `text` (str): Response body as text
- `headers` (dict): Response headers

### Methods

#### `.json()`

Parse response body as JSON.

```python
def json() -> JSONResponse.Value
```

**Returns:** Parsed JSON data (dict, list, etc.)

**Example:**
```python
@app.get(url="https://api.example.com/data")
async def handle_response(resp: Response):
    data = resp.json()
    return f"Received {len(data)} items"
```

**Raises:** `json.JSONDecodeError` if response is not valid JSON

#### `.__repr__()`

String representation of the response.

```python
def __repr__() -> str
```

**Example:**
```python
print(resp)  # <Response [200]>
```

## 🛣️ Route Class

Internal class representing a registered route. Usually you won't interact with this directly.

### Attributes

- `method` (str): HTTP method (GET, POST, etc.)
- `url` (str): Target URL
- `handler` (Callable): Handler function
- `params` (dict): Query parameters
- `json` (dict): JSON data
- `data` (dict): Form data

## ⚙️ Configuration Options

### Request Configuration

Each request type can be configured with:

```python
{
    "headers": {
        "User-Agent": "MyApp/1.0",
        "Authorization": "Bearer token",
        "Content-Type": "application/json",
    },
    "timeout": 30,  # Request timeout in seconds
    "allow_redirects": True,
}
```

#### Headers

Custom headers for requests:

```python
app = FastHTTP(
    get_request={
        "headers": {
            "User-Agent": "MyApp/1.0",
            "X-Custom-Header": "value",
        }
    }
)
```

#### Timeout

Request timeout in seconds:

```python
app = FastHTTP(
    get_request={"timeout": 10}  # 10 second timeout
)
```

### Global vs Per-Request Configuration

#### Global Configuration
```python
# Applies to all GET requests
app = FastHTTP(
    get_request={
        "headers": {"User-Agent": "Global/1.0"},
        "timeout": 5,
    }
)

@app.get(url="https://example.com")  # Uses global config
async def handler(resp: Response):
    return resp.status
```

#### Per-Request Override
```python
# Override specific request
@app.get(
    url="https://example.com",
    params={"custom": "param"}  # Additional params
)
async def handler(resp: Response):
    return resp.status
```

## 📊 Logging

### Log Levels

#### Info Level (Default)
Shows basic request/response information:
```
16:09:18.955 │ INFO     │ fasthttp │ ✔ FastHTTP started
16:09:19.520 │ INFO     │ fasthttp │ ✔ ✔️ GET     https://api.example.com  200 458.26ms
```

#### Debug Level
Shows detailed information including headers and response content:
```python
app = FastHTTP(debug=True)
```

Shows:
- Request headers
- Response headers  
- Response body (truncated)
- Handler results

### Log Format

```
TIME       │ LEVEL    │ LOGGER   │ MESSAGE
HH:MM:SS.mmm │ DEBUG   │ fasthttp │ 🐛 Registered route: GET https://example.com
HH:MM:SS.mmm │ INFO    │ fasthttp │ ✔ FastHTTP started
HH:MM:SS.mmm │ DEBUG   │ fasthttp │ 🐛 → GET https://example.com | headers={...}
HH:MM:SS.mmm │ INFO    │ fasthttp │ ✔ ← GET https://example.com [200] 123.45ms
HH:MM:SS.mmm │ DEBUG   │ fasthttp │ ↳ {"key": "value"}
```

### Icons

- 🐛 DEBUG level
- ✔ INFO level  
- ⚠ WARNING level
- ✖ ERROR level
- 💀 CRITICAL level

## 🔧 Error Handling

### Connection Errors
```python
try:
    app.run()
except aiohttp.ClientConnectionError as e:
    print(f"Connection error: {e}")
```

### Timeout Errors
Timeouts are handled automatically and logged as errors.

### Handler Exceptions
Exceptions in handler functions are caught and logged:
```
16:09:20.037 │ ERROR    │ fasthttp │ Handler exception in get_user: JSON decode error
```

## 📈 Performance Tips

### Batch Requests
Register multiple requests and run them together:
```python
# All requests run concurrently
@app.get(url="https://api1.com/data")
async def handler1(resp: Response): ...

@app.get(url="https://api2.com/data") 
async def handler2(resp: Response): ...

@app.get(url="https://api3.com/data")
async def handler3(resp: Response): ...

app.run()  # Runs all 3 requests concurrently
```

### Request Delays
Small delays (0.5s) are automatically added between requests to avoid overwhelming servers.

### Async Performance
Built on aiohttp for high-performance async operations.

---

*For more examples, see [Examples](examples.md)* 📚

# Dependencies

Dependencies are a powerful and intuitive way to modify requests before sending them. Unlike middleware, dependencies are applied to specific requests, not globally to the entire application.

## What is Dependency Injection?

In programming, "Dependency Injection" means that your code (in our case — request handlers) can declare what it needs to work, and the system will take care of providing these dependencies.

This is very useful for:

- Common logic (repetitive code)
- Shared database connections
- Security and authentication
- Logging and tracing
- And much more...

This way you avoid code duplication.

## Quick Example

Let's start with a simple example:

```python
from fasthttp import FastHTTP, Depends
from fasthttp.response import Response

app = FastHTTP()


async def add_auth_header(route, config):
    """Adds authorization header."""
    config.setdefault("headers", {})["Authorization"] = "Bearer my-token"
    return config


@app.get(
    url="https://api.example.com/users",
    dependencies=[Depends(add_auth_header)]
)
async def get_users(resp: Response):
    return resp.json()
```

When running, `add_auth_header` will execute before the request and add the token to the headers.

## Why Dependencies Instead of Middleware?

| Feature | Middleware | Dependencies |
|---------|------------|--------------|
| Global application | ✅ Yes | ❌ No |
| Application to specific request | ❌ No | ✅ Yes |
| Implementation complexity | Higher | Lower |
| Can modify response | ✅ Yes | ❌ No |
| Can return arbitrary value | ❌ No | ✅ Yes |

### When to Use Middleware

- Need to apply logic to absolutely all requests
- Requires response modification after request
- Need centralized error handling

### When to Use Dependencies

- Logic is only needed for specific requests
- Simple request configuration modification
- More declarative and clearer code

## Creating a Dependency

A dependency is an async function with two parameters:

```python
async def my_dependency(route, config):
    # route — route information
    # config — request configuration
    
    # Modify config
    config.setdefault("headers", {})["X-Custom"] = "value"
    
    # Return modified config
    return config
```

### Available route Parameters

The `route` object contains all information about the request:

```python
route.method      # HTTP method: "GET", "POST", "PUT", "PATCH", "DELETE"
route.url         # Full request URL
route.params      # Query parameters (dictionary)
route.json        # JSON request body (dictionary)
route.data        # Raw data
route.tags        # Request tags (list)
route.dependencies  # List of route dependencies
route.handler     # Response handler
route.response_model  # Pydantic model for validation
```

### Available config Parameters

The `config` object contains request settings:

```python
config.get("headers", {})      # Request headers
config.get("timeout", 30.0)    # Timeout in seconds
config.get("allow_redirects", True)  # Allow redirects
```

## Depends Function Parameters

The `Depends()` function accepts additional parameters:

```python
Depends(
    func,              # Your async dependency function
    use_cache=True,    # Cache result
    scope="function"   # Scope: "function" or "request"
)
```

### use_cache Parameter

If `use_cache=True` (default), the dependency result is cached for the duration of the request. This is useful for expensive computations that don't need to run multiple times:

```python
async def get_token(route, config):
    # Expensive operation - for example, request to another API
    token = await fetch_token_from_auth_server()
    config["headers"]["Authorization"] = f"Bearer {token}"
    return config


# Token will be obtained once and used for all requests
@app.get(url="/api/data", dependencies=[Depends(get_token, use_cache=True)])
async def handler1(resp): ...


@app.get(url="/api/other", dependencies=[Depends(get_token, use_cache=True)])
async def handler2(resp): ...
```

### scope Parameter

The `scope` parameter determines when the dependency is executed:

- `"function"` (default) — executes before the request handler
- `"request"` — executes around the entire request-response cycle

```python
async def log_request(route, config):
    print(f"Request start: {route.method} {route.url}")
    return config


# scope="function" — will execute only before the request
@app.get(url="/data", dependencies=[Depends(log_request, scope="function")])
async def handler(resp): ...
```

## Practical Examples

### Example 1: Adding Authorization Token

The most common use case is adding a token:

```python
async def add_bearer_token(route, config):
    """Adds Bearer token to request headers."""
    token = "your-secret-token"
    config.setdefault("headers", {})["Authorization"] = f"Bearer {token}"
    return config


@app.get(
    url="https://api.example.com/users",
    dependencies=[Depends(add_bearer_token)]
)
async def get_users(resp: Response):
    """Get list of users."""
    return resp.json()


@app.post(
    url="https://api.example.com/users",
    json={"name": "John", "email": "john@example.com"},
    dependencies=[Depends(add_bearer_token)]
)
async def create_user(resp: Response):
    """Create new user."""
    return resp.json()
```

### Example 2: Trace ID for Tracing

Adding a unique ID for request tracking:

```python
import uuid


async def add_trace_id(route, config):
    """Adds unique Trace ID for distributed tracing."""
    trace_id = str(uuid.uuid4())
    config.setdefault("headers", {})["X-Trace-ID"] = trace_id
    
    # Also can add start_time for time measurement
    import time
    config["_start_time"] = time.time()
    
    return config


@app.get(
    url="https://api.example.com/data",
    dependencies=[Depends(add_trace_id)]
)
async def get_data(resp: Response):
    return resp.json()
```

### Example 3: Multiple Dependencies

Dependencies are executed in order, like a chain:

```python
async def add_auth(route, config):
    """Adds authorization token."""
    config.setdefault("headers", {})["Authorization"] = "Bearer token"
    return config


async def add_trace(route, config):
    """Adds Trace ID."""
    config.setdefault("headers", {})["X-Trace-ID"] = "123"
    return config


async def add_custom(route, config):
    """Adds custom header."""
    config.setdefault("headers", {})["X-Custom-Header"] = "value"
    return config


@app.get(
    url="https://api.example.com/data",
    dependencies=[
        Depends(add_auth),      # Executes first
        Depends(add_trace),     # Second
        Depends(add_custom),    # Third
    ]
)
async def handler(resp: Response):
    # All headers will be added in order
    return resp.json()
```

### Example 4: Dynamic Headers Based on URL

You can analyze the URL and add different headers:

```python
async def add_api_version(route, config):
    """Adds API version to headers based on URL."""
    headers = config.setdefault("headers", {})
    
    if "/v2/" in route.url:
        headers["X-API-Version"] = "v2"
        headers["Accept"] = "application/vnd.api.v2+json"
    else:
        headers["X-API-Version"] = "v1"
        headers["Accept"] = "application/json"
    
    return config


@app.get(
    url="https://api.example.com/v2/users",
    dependencies=[Depends(add_api_version)]
)
async def get_users_v2(resp: Response):
    return resp.json()


@app.get(
    url="https://api.example.com/v1/users",
    dependencies=[Depends(add_api_version)]
)
async def get_users_v1(resp: Response):
    return resp.json()
```

### Example 5: Adding Query Parameters

Dependency can modify query parameters:

```python
async def add_pagination(route, config):
    """Adds default pagination parameters."""
    route.params = route.params or {}
    route.params.setdefault("page", 1)
    route.params.setdefault("limit", 10)
    
    # Limit maximum limit
    if route.params.get("limit", 10) > 100:
        route.params["limit"] = 100
    
    return config


@app.get(
    url="https://api.example.com/users",
    params={"name": "John"},  # already has parameters
    dependencies=[Depends(add_pagination)]
)
async def get_users(resp: Response):
    # Actual URL will be: /users?name=John&page=1&limit=10
    return resp.json()
```

### Example 6: Request Logging

Simple way to log requests:

```python
import time


async def log_request(route, config):
    """Logs request information."""
    print(f"🚀 Sending: {route.method} {route.url}")
    config["_start_time"] = time.time()
    return config


@app.get(
    url="https://api.example.com/data",
    dependencies=[Depends(log_request)]
)
async def handler(resp: Response):
    return resp.json()
```

### Example 7: Conditional Headers

Adding headers based on conditions:

```python
async def add_conditional_headers(route, config):
    """Adds different headers depending on method."""
    headers = config.setdefault("headers", {})
    
    if route.method == "POST":
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "application/json"
    elif route.method == "GET":
        headers["Accept"] = "application/json"
    
    return config


@app.post(
    url="https://api.example.com/data",
    json={"test": "value"},
    dependencies=[Depends(add_conditional_headers)]
)
async def create_data(resp: Response):
    return resp.json()
```

### Example 8: Working with Cache

Using use_cache for expensive operations:

```python
import aiohttp


async def get_oauth_token(route, config):
    """Gets OAuth token (expensive operation)."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://auth.example.com/token",
            json={"client_id": "my_app", "client_secret": "secret"}
        ) as resp:
            data = await resp.json()
            token = data["access_token"]
    
    config.setdefault("headers", {})["Authorization"] = f"Bearer {token}"
    return config


# Token will be obtained once and used for all requests
@app.get(
    url="https://api.example.com/users",
    dependencies=[Depends(get_oauth_token, use_cache=True)]
)
async def get_users(resp: Response):
    return resp.json()


@app.get(
    url="https://api.example.com/posts",
    dependencies=[Depends(get_oauth_token, use_cache=True)]
)
async def get_posts(resp: Response):
    return resp.json()
```

### Example 9: Validation Before Request

You can even validate data before sending:

```python
async def validate_api_key(route, config):
    """Validates API key presence."""
    api_key = config.get("headers", {}).get("X-API-Key")
    
    if not api_key:
        raise ValueError("API Key required")
    
    # Can even validate key validity
    if not is_valid_key(api_key):
        raise ValueError("Invalid API Key")
    
    return config


@app.get(
    url="https://api.example.com/data",
    get_request={"headers": {"X-API-Key": "my-key"}},
    dependencies=[Depends(validate_api_key)]
)
async def get_data(resp: Response):
    return resp.json()
```

## Using Depends Without Parentheses

You can pass a function directly to Depends:

```python
async def add_auth(route, config):
    config.setdefault("headers", {})["Authorization"] = "Bearer token"
    return config


# Both variants work the same
@app.get(url="/test1", dependencies=[Depends(add_auth)])
async def test1(resp): ...


@app.get(url="/test2", dependencies=[add_auth])  # Same!
async def test2(resp): ...
```

## Combining with Tags

Dependencies work great with tags:

```python
async def add_auth(route, config):
    config.setdefault("headers", {})["Authorization"] = "Bearer token"
    return config


@app.get(
    url="https://api.example.com/users",
    tags=["users", "v1"],
    dependencies=[Depends(add_auth)]
)
async def get_users(resp): ...


@app.get(
    url="https://api.example.com/posts",
    tags=["posts", "v1"],
    dependencies=[Depends(add_auth)]
)
async def get_posts(resp): ...


# Run only users
app.run(tags=["users"])
```

## See Also

- [Middleware](middleware.md) — for global logic
- [Configuration](configuration.md) — default settings
- [Quick Start](quick-start.md) — FastHTTP basics

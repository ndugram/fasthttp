# Creating Middleware

Learn how to create custom middleware.

## Base Class

Create a class inheriting from `BaseMiddleware`:

```python
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware
from fasthttp.response import Response


class MyMiddleware(BaseMiddleware):
    async def before_request(self, route, config):
        """Executed before each request."""
        return config

    async def after_response(self, response, route, config):
        """Executed after each response."""
        return response

    async def on_error(self, error, route, config):
        """Executed on error."""
        raise error
```

## Method Signatures

### before_request(route, config)

Called before sending each request.

**Parameters:**
- `route` - Route information
- `config` - Request configuration

**Returns:** Modified `config`

### after_response(response, route, config)

Called after receiving a response.

**Parameters:**
- `response` - Response object
- `route` - Route information
- `config` - Request configuration

**Returns:** Modified `response`

### on_error(error, route, config)

Called when an error occurs.

**Parameters:**
- `error` - Exception
- `route` - Route information
- `config` - Request configuration

**Can:** Handle error or re-raise

## Using Middleware

```python
app = FastHTTP(middleware=[MyMiddleware()])
```

## Multiple Middleware

Execution order - first added executes first:

```python
app = FastHTTP(middleware=[
    AuthMiddleware(),
    LoggingMiddleware(),
    MetricsMiddleware(),
])
```

## Route Object Attributes

```python
route.method      # HTTP method
route.url         # Request URL
route.params      # Query parameters
route.json        # JSON body
route.tags        # Tags
```

## Config Object Keys

```python
config.get("headers", {})      # Request headers
config.get("timeout", 30.0)    # Timeout
config.get("allow_redirects", True)
```

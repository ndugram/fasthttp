# Middleware Reference

Middleware classes reference.

## BaseMiddleware

Base class for creating middleware:

```python
from fasthttp.middleware import BaseMiddleware


class MyMiddleware(BaseMiddleware):
    async def before_request(self, route, config):
        return config
    
    async def after_response(self, response, route, config):
        return response
    
    async def on_error(self, error, route, config):
        raise error
```

## Methods

### before_request(route, config)

Called before each request.

**Parameters:**
- `route` - Route information
- `config` - Request configuration

**Returns:** Modified config

### after_response(response, route, config)

Called after each response.

**Parameters:**
- `response` - Response object
- `route` - Route information
- `config` - Request configuration

**Returns:** Modified response

### on_error(error, route, config)

Called on error.

**Parameters:**
- `error` - Exception
- `route` - Route information
- `config` - Request configuration

**Can:** Handle or re-raise error

## CacheMiddleware

Built-in caching middleware:

```python
from fasthttp import CacheMiddleware

app = FastHTTP(
    middleware=[CacheMiddleware(ttl=3600, max_size=100)]
)
```

**Parameters:**
- `ttl` - Cache time-to-live (seconds)
- `max_size` - Maximum cached requests

## MiddlewareManager

Manages middleware execution:

```python
from fasthttp.middleware import MiddlewareManager

manager = MiddlewareManager([middleware1, middleware2])
```

# Middleware

Middleware allows you to intercept and modify HTTP requests and responses in FastHTTP. This is useful for adding authentication, logging, error handling, and other cross-cutting concerns.

## What is Middleware?

Middleware is a class that hooks into the request lifecycle. You can use it to execute code before sending a request, after receiving a response, or when an error occurs.

## Creating Middleware

To create middleware, inherit from `BaseMiddleware` and override the methods you need:

```python
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware
from fasthttp.response import Response
from fasthttp.routing import Route
from fasthttp.types import RequestsOptinal


class LoggingMiddleware(BaseMiddleware):
    async def before_request(
        self, route: Route, config: RequestsOptinal
    ) -> RequestsOptinal:
        print(f"Sending {route.method} to {route.url}")
        return config

    async def after_response(
        self, response: Response, route: Route, config: RequestsOptinal
    ) -> Response:
        print(f"Received response: {response.status}")
        return response


app = FastHTTP(middleware=[LoggingMiddleware()])


@app.get(url="https://httpbin.org/get")
async def get_data(resp: Response):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

## Middleware Methods

### before_request

Called before sending the HTTP request. Use this to modify request headers, add authentication, or log outgoing requests.

```python
async def before_request(
    self, route: Route, config: RequestsOptinal
) -> RequestsOptinal:
    headers = config.get("headers", {})
    headers["Authorization"] = "Bearer token"
    config["headers"] = headers
    return config
```

### after_response

Called after receiving a successful response. Use this to transform response data, log metrics, or cache responses.

```python
async def after_response(
    self, response: Response, route: Route, config: RequestsOptinal
) -> Response:
    json_data = response.json()
    json_data["custom_field"] = "value"
    response.text = json.dumps(json_data)
    return response
```

### on_error

Called when an error occurs during the request. Use this for custom error logging or error tracking.

```python
async def on_error(
    self, error: Exception, route: Route, config: RequestsOptinal
) -> None:
    print(f"Error on {route.url}: {error}")
```

## Using Multiple Middleware

You can use multiple middleware instances. They will be executed in the order you provide them.

```python
app = FastHTTP(
    middleware=[
        AuthMiddleware(),
        LoggingMiddleware(),
        ErrorTrackingMiddleware()
    ]
)
```

## Common Use Cases

### Authentication

Add authentication headers to all requests:

```python
class AuthMiddleware(BaseMiddleware):
    def __init__(self, token: str):
        self.token = token

    async def before_request(
        self, route: Route, config: RequestsOptinal
    ) -> RequestsOptinal:
        headers = config.get("headers", {})
        headers["Authorization"] = f"Bearer {self.token}"
        config["headers"] = headers
        return config
```

### Logging

Log all requests and responses:

```python
class LoggingMiddleware(BaseMiddleware):
    async def before_request(
        self, route: Route, config: RequestsOptinal
    ) -> RequestsOptinal:
        print(f"Request: {route.method} {route.url}")
        return config

    async def after_response(
        self, response: Response, route: Route, config: RequestsOptinal
    ) -> Response:
        print(f"Response: {response.status}")
        return response
```

### Error Tracking

Track and log errors:

```python
class ErrorTrackingMiddleware(BaseMiddleware):
    async def on_error(
        self, error: Exception, route: Route, config: RequestsOptinal
    ) -> None:
        print(f"Error: {error.__class__.__name__} on {route.url}")
```

### Request ID

Add unique request IDs for tracing:

```python
import uuid


class RequestIDMiddleware(BaseMiddleware):
    async def before_request(
        self, route: Route, config: RequestsOptinal
    ) -> RequestsOptinal:
        headers = config.get("headers", {})
        headers["X-Request-ID"] = str(uuid.uuid4())
        config["headers"] = headers
        return config
```

## Middleware Execution Order

Middleware is executed in the order they are provided:

1. Before request: Middleware[0] -> Middleware[1] -> ... -> Middleware[n]
2. After response: Middleware[0] -> Middleware[1] -> ... -> Middleware[n]
3. On error: Middleware[0] -> Middleware[1] -> ... -> Middleware[n]

Each middleware receives the result from the previous middleware, allowing you to chain transformations.

## Best Practices

1. Keep middleware focused on a single responsibility
2. Return the modified config or response object
3. Handle exceptions in middleware methods
4. Use middleware for cross-cutting concerns
5. Test middleware independently

## Response Caching (CacheMiddleware)

CacheMiddleware stores HTTP responses in memory so you don't need to make repeated requests to the server. This is useful when you frequently request the same data.

**Why use it?**
- Reduces API load
- Responses return instantly (from cache)
- Saves bandwidth

**How it works:**
1. First request → goes to server → saved to cache
2. Second request (within TTL) → returns from cache
3. After 1 hour (TTL) → new request to server

### Example

```python
from fasthttp import FastHTTP, CacheMiddleware
from fasthttp.response import Response

# Create app with caching (TTL: 1 hour, max: 100 responses)
app = FastHTTP(
    middleware=[CacheMiddleware(ttl=3600, max_size=100)]
)


@app.get(url="https://api.example.com/users")
async def get_users(resp: Response):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

Now all GET requests will be cached for 1 hour. If you request `/users` again within that hour — the response will return instantly from cache.

---

For more examples, see the [Examples](examples.md) section.

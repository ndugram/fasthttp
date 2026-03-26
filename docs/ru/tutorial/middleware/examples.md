# Примеры Middleware

Практические примеры middleware.

## Аутентификация

```python
from fasthttp.middleware import BaseMiddleware


class AuthMiddleware(BaseMiddleware):
    def __init__(self, token: str):
        self.token = token

    async def before_request(self, route, config):
        headers = config.get("headers", {})
        headers["Authorization"] = f"Bearer {self.token}"
        config["headers"] = headers
        return config


app = FastHTTP(middleware=[AuthMiddleware(token="your-token")])
```

## Логирование

```python
import time
from fasthttp.middleware import BaseMiddleware


class LoggingMiddleware(BaseMiddleware):
    async def before_request(self, route, config):
        print(f"Отправка: {route.method} {route.url}")
        config["_start_time"] = time.time()
        return config

    async def after_response(self, response, route, config):
        start_time = config.get("_start_time", 0)
        duration = time.time() - start_time
        print(f"Ответ: {route.method} {route.url} - {response.status} ({duration:.2f}s)")
        return response


app = FastHTTP(middleware=[LoggingMiddleware()])
```

## Trace ID

```python
import uuid
from fasthttp.middleware import BaseMiddleware


class TraceMiddleware(BaseMiddleware):
    async def before_request(self, route, config):
        trace_id = str(uuid.uuid4())
        headers = config.get("headers", {})
        headers["X-Trace-ID"] = trace_id
        config["headers"] = headers
        return config


app = FastHTTP(middleware=[TraceMiddleware()])
```

## Кеширование

FastHTTP включает встроенный `CacheMiddleware`:

```python
from fasthttp import CacheMiddleware

app = FastHTTP(middleware=[
    CacheMiddleware(ttl=3600, max_size=100)
])
```

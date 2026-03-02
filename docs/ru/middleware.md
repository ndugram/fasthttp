# Middleware

Перехват и модификация запросов/ответов.

## Создание

```python
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware
from fasthttp.response import Response


class MyMiddleware(BaseMiddleware):
    async def before_request(self, route, config):
        # изменить конфиг до запроса
        return config

    async def after_response(self, response, route, config):
        # изменить ответ после запроса
        return response

    async def on_error(self, error, route, config):
        # обработать ошибку
        pass
```

## Использование

```python
app = FastHTTP(middleware=MyMiddleware())
```

Несколько middleware — выполняются по порядку:

```python
app = FastHTTP(middleware=[
    AuthMiddleware(),
    LoggingMiddleware(),
])
```

## Примеры

### Аутентификация

```python
class AuthMiddleware(BaseMiddleware):
    def __init__(self, token: str):
        self.token = token

    async def before_request(self, route, config):
        headers = config.get("headers", {})
        headers["Authorization"] = f"Bearer {self.token}"
        config["headers"] = headers
        return config
```

### ID запроса

```python
import uuid


class RequestIDMiddleware(BaseMiddleware):
    async def before_request(self, route, config):
        headers = config.get("headers", {})
        headers["X-Request-ID"] = str(uuid.uuid4())
        config["headers"] = headers
        return config
```

### Кеширование

```python
from fasthttp import CacheMiddleware

app = FastHTTP(middleware=[CacheMiddleware(ttl=3600, max_size=100)])
```

Кеширует GET запросы на 1 час.

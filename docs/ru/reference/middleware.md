# Справочник Middleware

Справочник по классам middleware.

## BaseMiddleware

Базовый класс для создания middleware:

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

## Методы

### before_request(route, config)

Вызывается перед каждым запросом.

### after_response(response, route, config)

Вызывается после каждого ответа.

### on_error(error, route, config)

Вызывается при ошибке.

## CacheMiddleware

Встроенный middleware для кеширования:

```python
from fasthttp import CacheMiddleware

app = FastHTTP(middleware=[CacheMiddleware(ttl=3600, max_size=100)])
```

- `ttl` - время жизни кэша (секунды)
- `max_size` - максимальное количество закэшированных запросов

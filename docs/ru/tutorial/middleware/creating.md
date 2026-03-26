# Создание Middleware

Узнайте, как создавать собственное middleware.

## Базовый класс

Создайте класс, наследующий от `BaseMiddleware`:

```python
from fasthttp.middleware import BaseMiddleware


class MyMiddleware(BaseMiddleware):
    async def before_request(self, route, config):
        # Выполняется перед каждым запросом
        return config

    async def after_response(self, response, route, config):
        # Выполняется после каждого ответа
        return response

    async def on_error(self, error, route, config):
        # Выполняется при ошибке
        raise error
```

## Использование

```python
app = FastHTTP(middleware=[MyMiddleware()])
```

## Несколько Middleware

Порядок выполнения - первый добавленный выполняется первым:

```python
app = FastHTTP(middleware=[
    AuthMiddleware(),
    LoggingMiddleware(),
    MetricsMiddleware(),
])
```

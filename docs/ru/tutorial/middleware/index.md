# Middleware

Middleware позволяет добавлять глобальную логику для всех запросов.

## Обзор

- [Создание Middleware](creating.md) - Как создавать собственное middleware
- [Примеры](examples.md) - Практические примеры middleware

## Быстрый пример

```python
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware


class MyMiddleware(BaseMiddleware):
    async def before_request(self, route, config):
        config.setdefault("headers", {})["X-Custom"] = "value"
        return config

    async def after_response(self, response, route, config):
        return response


app = FastHTTP(middleware=[MyMiddleware()])
```

## Жизненный цикл

```
before_request -> [Отправка запроса] -> after_response
                    или
                 on_error
```

## Сравнение с зависимостями

| Функция | Middleware | Зависимости |
|---------|------------|-------------|
| Глобальное применение | Да | Нет |
| Конкретный запрос | Нет | Да |
| Может модифицировать ответ | Да | Нет |
| Обработка ошибок | Да | Нет |

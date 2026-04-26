# Middleware

Middleware позволяет перехватывать и модифицировать **каждый запрос и ответ** через `FastHTTP` — без изменения кода обработчиков.

## Что может делать middleware

- Автоматически добавлять заголовки авторизации
- Логировать все запросы и ответы
- Добавлять заголовки таймингов и трейсинга
- Трансформировать данные ответа
- Отслеживать ошибки и метрики

## Как работает

```
запрос →  mw1.request → mw2.request → mw3.request → [HTTP]
ответ  ←  mw1.response ← mw2.response ← mw3.response ← [HTTP]
```

Middleware выполняется в порядке `__priority__` на входе и в **обратном порядке** на выходе.

## Быстрый пример

```python
import asyncio
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware
from fasthttp.response import Response


class LoggingMiddleware(BaseMiddleware):
    __return_type__ = None
    __priority__ = 0
    __methods__ = None
    __enabled__ = True

    async def request(self, method, url, kwargs):
        print(f"→ {method} {url}")
        return kwargs

    async def response(self, response):
        print(f"← {response.status}")
        return response


app = FastHTTP(middleware=[LoggingMiddleware()])
```

Вывод:

```
→ GET https://httpbin.org/get
← 200
```

## Далее

- [Создание Middleware](creating.md) — API BaseMiddleware, атрибуты класса, pipe-чейнинг
- [Примеры](examples.md) — auth, логирование, тайминги, фильтр по методам, toggle

## Сравнение с зависимостями

| Функция | Middleware | Зависимости |
|---------|------------|-------------|
| Глобальное применение | Да | Нет |
| Конкретный запрос | Нет | Да |
| Может модифицировать ответ | Да | Нет |
| Обработка ошибок | Да | Нет |

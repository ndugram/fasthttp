# Middleware

Middleware (промежуточное ПО) позволяет добавлять глобальную логику, которая будет выполняться для всех запросов.

## Введение

Middleware в FastHTTP работает похоже на middleware в FastAPI, но предназначено для исходящих запросов. Оно позволяет:

- Модифицировать запросы перед отправкой
- Модифицировать ответы после получения
- Обрабатывать ошибки
- Добавлять логирование
- Добавлять аутентификацию

## Создание Middleware

Создайте класс, наследующий от `BaseMiddleware`:

```python
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware
from fasthttp.response import Response


class MyMiddleware(BaseMiddleware):
    async def before_request(self, route, config):
        """Выполняется перед каждым запросом."""
        # Модифицируем config
        config.setdefault("headers", {})["X-Custom"] = "value"
        return config

    async def after_response(self, response, route, config):
        """Выполняется после каждого ответа."""
        # Модифицируем response
        return response

    async def on_error(self, error, route, config):
        """Выполняется при ошибке."""
        print(f"Ошибка: {error}")
        raise error
```

## Использование Middleware

```python
from fasthttp import FastHTTP

app = FastHTTP(middleware=MyMiddleware())
```

### Несколько Middleware

Порядок выполнения — первый добавленный выполняется первым:

```python
app = FastHTTP(middleware=[
    AuthMiddleware(),
    LoggingMiddleware(),
    MetricsMiddleware(),
])
```

## Примеры Middleware

### Аутентификация

```python
from fasthttp import FastHTTP
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

### Добавление Trace ID

```python
import uuid
from fasthttp import FastHTTP
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

### Логирование

```python
import time
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware


class LoggingMiddleware(BaseMiddleware):
    async def before_request(self, route, config):
        print(f"🚀 Отправка: {route.method} {route.url}")
        config["_start_time"] = time.time()
        return config

    async def after_response(self, response, route, config):
        start_time = config.get("_start_time", 0)
        duration = time.time() - start_time
        print(f"✅ Ответ: {route.method} {route.url} - {response.status} ({duration:.2f}s)")
        return response


app = FastHTTP(middleware=[LoggingMiddleware()])
```

### Кеширование

FastHTTP поставляется с встроенным CacheMiddleware:

```python
from fasthttp import FastHTTP, CacheMiddleware

app = FastHTTP(middleware=[
    CacheMiddleware(ttl=3600, max_size=100)  # TTL в секундах, макс. размер кэша
])
```

Кеширует GET запросы в памяти.

### Rate Limiting

```python
import time
from collections import defaultdict
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, max_requests: int = 10, window: int = 60):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)

    async def before_request(self, route, config):
        now = time.time()
        host = config.get("headers", {}).get("Host", "default")
        
        # Очищаем старые запросы
        self.requests[host] = [
            t for t in self.requests[host] 
            if now - t < self.window
        ]
        
        # Проверяем лимит
        if len(self.requests[host]) >= self.max_requests:
            raise Exception(f"Rate limit exceeded: {self.max_requests} requests per {self.window}s")
        
        self.requests[host].append(now)
        return config


app = FastHTTP(middleware=[RateLimitMiddleware(max_requests=10, window=60)])
```

### Модификация ответа

```python
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware


class ResponseModifierMiddleware(BaseMiddleware):
    async def after_response(self, response, route, config):
        # Добавляем заголовки в ответ
        response.headers["X-Custom-Response"] = "value"
        return response


app = FastHTTP(middleware=[ResponseModifierMiddleware()])
```

## Жизненный цикл Middleware

```
before_request → [Отправка запроса] → after_response
                    или
                 on_error
```

### before_request(route, config)

Вызывается перед отправкой каждого запроса. Может модифицировать `config`.

**Параметры:**
- `route` — информация о маршруте
- `config` — конфигурация запроса

**Возвращает:** модифицированный `config`

### after_response(response, route, config)

Вызывается после получения ответа. Может модифицировать `response`.

**Параметры:**
- `response` — объект ответа
- `route` — информация о маршруте
- `config` — конфигурация запроса

**Возвращает:** модифицированный `response`

### on_error(error, route, config)

Вызывается при возникновении ошибки.

**Параметры:**
- `error` — исключение
- `route` — информация о маршруте
- `config` — конфигурация запроса

**Может:**
- Обработать ошибку и вернуть значение
- Пробросить ошибку дальше

## Сравнение с Dependencies

| Особенность | Middleware | Dependencies |
|-------------|------------|--------------|
| Глобальное применение | ✅ Да | ❌ Нет |
| Применение к конкретному запросу | ❌ Нет | ✅ Да |
| Модификация response | ✅ Да | ❌ Нет |
| Обработка ошибок | ✅ Да | ❌ Нет |
| Сложность | Выше | Ниже |

## Смотрите также

- [Зависимости](dependencies.md) — для конкретных запросов
- [Конфигурация](configuration.md) — настройки
- [Быстрый старт](quick-start.md) — основы

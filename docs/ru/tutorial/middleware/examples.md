# Примеры Middleware

## Auth middleware

Добавляет Bearer-токен в каждый запрос:

```python
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware


class BearerAuthMiddleware(BaseMiddleware):
    __return_type__ = bool
    __priority__ = 0
    __methods__ = None
    __enabled__ = True

    def __init__(self, token: str) -> None:
        self.token = token

    async def request(self, method, url, kwargs):
        kwargs["headers"] = kwargs.get("headers") or {}
        kwargs["headers"]["Authorization"] = f"Bearer {self.token}"
        return kwargs


app = FastHTTP(middleware=[BearerAuthMiddleware("my-secret-token")])
```

## Logging middleware

Выводит каждый запрос и ответ:

```python
from fasthttp.middleware import BaseMiddleware


class LoggingMiddleware(BaseMiddleware):
    __return_type__ = None
    __priority__ = 99
    __methods__ = None
    __enabled__ = True

    async def request(self, method, url, kwargs):
        print(f"→ {method} {url}")
        return kwargs

    async def response(self, response):
        print(f"← {response.status}")
        return response
```

!!! tip
    Высокий `__priority__` — logging запускается **последним на входе** (видит финальные kwargs)
    и **первым на выходе** (видит сырой ответ).

## Timing middleware

Измеряет продолжительность запроса:

```python
import time
from contextvars import ContextVar
from fasthttp.middleware import BaseMiddleware


class TimingMiddleware(BaseMiddleware):
    __return_type__ = float
    __priority__ = 0
    __methods__ = None
    __enabled__ = True

    def __init__(self) -> None:
        self._start: ContextVar[float] = ContextVar("timing_start", default=0.0)

    async def request(self, method, url, kwargs):
        self._start.set(time.monotonic())
        return kwargs

    async def response(self, response):
        elapsed = time.monotonic() - self._start.get()
        print(f"Запрос занял {elapsed:.3f}s")
        return response
```

## Trace ID middleware

Добавляет уникальный ID к каждому запросу:

```python
import uuid
from fasthttp.middleware import BaseMiddleware


class TraceMiddleware(BaseMiddleware):
    __return_type__ = None
    __priority__ = 0
    __methods__ = None
    __enabled__ = True

    async def request(self, method, url, kwargs):
        kwargs["headers"] = kwargs.get("headers") or {}
        kwargs["headers"]["X-Trace-ID"] = str(uuid.uuid4())
        return kwargs
```

## Фильтр по методам

Запускает middleware только для определённых HTTP-методов:

```python
class WriteOpMiddleware(BaseMiddleware):
    __return_type__ = bool
    __priority__ = 1
    __methods__ = ["POST", "PUT", "PATCH", "DELETE"]
    __enabled__ = True

    async def request(self, method, url, kwargs):
        kwargs["headers"] = kwargs.get("headers") or {}
        kwargs["headers"]["X-Write-Op"] = "true"
        return kwargs
```

Для `GET`, `HEAD` и `OPTIONS` этот middleware молча пропускается.

## Toggle без удаления

Отключайте middleware в рантайме без редактирования приложения:

```python
debug = LoggingMiddleware()

app = FastHTTP(middleware=[debug])

# в какой-то момент отключаем
debug.__enabled__ = False   # не логируется

# включаем обратно
debug.__enabled__ = True    # снова логируется
```

## Цепочка через pipe

Объединяйте несколько middleware в одну строку:

```python
from fasthttp import FastHTTP
from fasthttp.middleware import MiddlewareChain

chain = (
    BearerAuthMiddleware("token")
    | TimingMiddleware()
    | LoggingMiddleware()
)

app = FastHTTP(middleware=chain)
```

Порядок выполнения на запросе: `BearerAuth → Timing → Logging → [HTTP]`  
Порядок выполнения на ответе: `[HTTP] → Logging → Timing → BearerAuth`

## Error tracking middleware

Считает ошибки и логирует контекст:

```python
from fasthttp.middleware import BaseMiddleware


class ErrorTrackingMiddleware(BaseMiddleware):
    __return_type__ = None
    __priority__ = 0
    __methods__ = None
    __enabled__ = True

    def __init__(self) -> None:
        self.error_count = 0

    async def on_error(self, error, route, config) -> None:
        self.error_count += 1
        print(f"Error #{self.error_count}: {error.__class__.__name__}")
        print(f"  {route.method} {route.url} — {error}")
```

## Кеширование

FastHTTP включает встроенный `CacheMiddleware`:

```python
from fasthttp import FastHTTP, CacheMiddleware

app = FastHTTP(
    middleware=[CacheMiddleware(ttl=3600, max_size=100)]
)
```

- `ttl` — время жизни кэша в секундах
- `max_size` — максимальное количество записей (LRU-вытеснение)
- `cache_methods` — список методов для кэширования (по умолчанию `["GET"]`)

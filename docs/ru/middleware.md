# Middleware

Middleware позволяет перехватывать и модифицировать каждый запрос и ответ через `FastHTTP` — без изменения кода обработчиков.

## Что может делать middleware

- Автоматически добавлять заголовки авторизации
- Логировать все запросы и ответы
- Добавлять заголовки таймингов и трейсинга
- Повторять запрос при определённых кодах ответа
- Трансформировать данные ответа

## Как работает

```
запрос →  mw1.request → mw2.request → mw3.request → [HTTP]
ответ  ←  mw1.response ← mw2.response ← mw3.response ← [HTTP]
```

Middleware выполняется в порядке `__priority__` на входе и в **обратном порядке** на выходе.

## Создание Middleware

Создайте класс, наследующий от `BaseMiddleware`:

```python
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware
from fasthttp.response import Response


class MyMiddleware(BaseMiddleware):
    __return_type__ = None
    __priority__ = 0
    __methods__ = None
    __enabled__ = True

    async def request(self, method, url, kwargs):
        kwargs["headers"] = kwargs.get("headers") or {}
        kwargs["headers"]["X-Custom"] = "value"
        return kwargs

    async def response(self, response):
        return response

    async def on_error(self, error, route, config):
        print(f"Ошибка: {error}")
```

## Подключение

=== "Список"

    ```python
    app = FastHTTP(middleware=[AuthMiddleware(), LoggingMiddleware()])
    ```

=== "Pipe"

    ```python
    app = FastHTTP(middleware=AuthMiddleware() | LoggingMiddleware())
    ```

=== "Один"

    ```python
    app = FastHTTP(middleware=MyMiddleware())
    ```

## Примеры

### Аутентификация

```python
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware


class AuthMiddleware(BaseMiddleware):
    __return_type__ = bool
    __priority__ = 0
    __methods__ = None
    __enabled__ = True

    def __init__(self, token: str):
        self.token = token

    async def request(self, method, url, kwargs):
        kwargs["headers"] = kwargs.get("headers") or {}
        kwargs["headers"]["Authorization"] = f"Bearer {self.token}"
        return kwargs


app = FastHTTP(middleware=[AuthMiddleware(token="your-token")])
```

### Добавление Trace ID

```python
import uuid
from fasthttp import FastHTTP
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


app = FastHTTP(middleware=[TraceMiddleware()])
```

### Логирование

```python
import time
from contextvars import ContextVar
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware


class LoggingMiddleware(BaseMiddleware):
    __return_type__ = None
    __priority__ = 99
    __methods__ = None
    __enabled__ = True

    def __init__(self) -> None:
        self._start: ContextVar[float] = ContextVar("log_start", default=0.0)

    async def request(self, method, url, kwargs):
        print(f"→ {method} {url}")
        self._start.set(time.monotonic())
        return kwargs

    async def response(self, response):
        elapsed = time.monotonic() - self._start.get()
        print(f"← {response.status} ({elapsed:.2f}s)")
        return response


app = FastHTTP(middleware=[LoggingMiddleware()])
```

### Кеширование

FastHTTP поставляется с встроенным `CacheMiddleware`:

```python
from fasthttp import FastHTTP, CacheMiddleware

app = FastHTTP(
    middleware=[CacheMiddleware(ttl=3600, max_size=100)]
)
```

Кэширует GET-запросы в памяти с LRU-вытеснением.

### Retry (Повторы)

FastHTTP поставляется с встроенным `RetryMiddleware` для автоматических повторов с экспоненциальной задержкой:

```python
from fasthttp import FastHTTP, RetryMiddleware

app = FastHTTP(
    middleware=RetryMiddleware(
        max_retries=3,
        retry_on={429, 500, 502, 503, 504},
        backoff_factor=0.5,
    )
)
```

Автоматически повторяет неудачные запросы при ошибках соединения, таймаутах или определённых HTTP-кодах.

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `max_retries` | `int` | `3` | Максимальное количество попыток повтора |
| `retry_on` | `set[int]` | `{429, 500, 502, 503, 504}` | HTTP-коды, вызывающие повтор |
| `backoff_factor` | `float` | `0.5` | Множитель для экспоненциальной задержки |
| `max_delay` | `float` | `30.0` | Максимальная задержка между повторами в секундах |
| `retry_exceptions` | `tuple[type[Exception], ...]` | `(Exception,)` | Типы исключений, вызывающие повтор |

### Модификация ответа

```python
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware


class ResponseModifierMiddleware(BaseMiddleware):
    __return_type__ = None
    __priority__ = 0
    __methods__ = None
    __enabled__ = True

    async def response(self, response):
        response.headers["X-Custom-Response"] = "value"
        return response


app = FastHTTP(middleware=[ResponseModifierMiddleware()])
```

## Атрибуты класса

| Атрибут | Тип | Описание |
|---------|-----|----------|
| `__return_type__` | `type \| None` | Тип, с которым работает middleware |
| `__priority__` | `int` | Порядок выполнения — **меньше = раньше** |
| `__methods__` | `list[str] \| None` | HTTP-методы для перехвата. `None` = все методы |
| `__enabled__` | `bool` | `False` пропускает без удаления из цепочки |

## Toggle в рантайме

```python
debug = LoggingMiddleware()
app = FastHTTP(middleware=[debug])

debug.__enabled__ = False   # отключить
debug.__enabled__ = True    # включить обратно
```

## Event Hooks

Event hooks — более простая альтернатива middleware для типовых задач: логирование, тайминг, обработка ошибок. Это декораторы на приложении, роутере или сессии.

### `on_request`

Вызывается перед каждым запросом:

```python
from fasthttp import FastHTTP

app = FastHTTP()

@app.on_request
async def log_request(route, config):
    print(f"→ {route.method} {route.url}")
```

### `on_response`

Вызывается после каждого успешного ответа:

```python
@app.on_response
async def log_response(response):
    print(f"← {response.status}")
```

### `on_error`

Вызывается при ошибке:

```python
@app.on_error
async def track_error(error, route):
    print(f"✖ {error} на {route.url}")
```

### `exception_handler`

Обработчик для конкретного типа исключения, в стиле FastAPI. В отличие от `on_error`, возвращаемое значение **заменяет результат route** вместо того, чтобы запрос просто тихо падал — запрос "восстанавливается", а не только логируется.

```python
from fasthttp.exceptions import FastHTTPTimeoutError

@app.exception_handler(FastHTTPTimeoutError)
async def handle_timeout(route, exc):
    return {"error": "timeout", "url": route.url}
```

Хендлер принимает `(route, exc)` — тот же порядок, что и `(request, exc)` в FastAPI. Если под исключение подходит несколько зарегистрированных хендлеров (через наследование), побеждает самый специфичный:

```python
@app.exception_handler(Exception)
async def fallback(route, exc):
    return {"error": "unexpected"}

@app.exception_handler(FastHTTPTimeoutError)
async def timeout(route, exc):
    return {"error": "timeout"}  # сработает для FastHTTPTimeoutError, fallback — для всего остального
```

До хендлера доходят только исключения, которые реально "вылетают" из запроса — для HTTP-статусов это значит, что у route (или у приложения) должен быть включён `raise_for_status=True`, иначе `FastHTTPBadStatusError` вообще не поднимается и перехватывать нечего.

### С Router

Event hooks роутера, включая `exception_handler`, мержатся в приложение через `include_router()`:

```python
from fasthttp import FastHTTP, Router

router = Router(base_url="https://api.example.com")

@router.on_request
async def router_hook(route, config):
    print(f"[router] → {route.url}")

@router.exception_handler(FastHTTPTimeoutError)
async def router_timeout(route, exc):
    return {"error": "timeout", "url": route.url}

app = FastHTTP()
app.include_router(router)
# оба хука будут вызываться для всех запросов этого роутера
```

### С AsyncSession

```python
from fasthttp import AsyncSession

async with AsyncSession() as session:
    @session.on_request
    async def inject_auth(route, config):
        config["headers"]["Authorization"] = "Bearer token"

    resp = await session.get("https://api.example.com")
```

`exception_handler` доступен только на `FastHTTP` и `Router` — `AsyncSession` его не поддерживает, так как возвращает ответы напрямую вызывающему коду, а не маршрутизирует их через хендлеры.

### Middleware vs Event Hooks

| Возможность | Middleware | Event Hooks |
|-------------|------------|-------------|
| Модификация запроса | ✅ Да | ✅ Да |
| Модификация ответа | ✅ Да | ❌ Нет |
| Обработка ошибок | ✅ Да | ✅ Да |
| Контроль порядка | ✅ Приоритет | ❌ Порядок регистрации |
| Фильтрация по методам | ✅ `__methods__` | ❌ Нет |
| Сложность | Выше | Ниже |

## Сравнение с Dependencies

| Особенность | Middleware | Dependencies |
|-------------|------------|--------------|
| Глобальное применение | ✅ Да | ❌ Нет |
| Применение к конкретному запросу | ❌ Нет | ✅ Да |
| Модификация response | ✅ Да | ❌ Нет |
| Обработка ошибок | ✅ Да | ❌ Нет |
| Сложность | Выше | Ниже |

## Смотрите также

- [Создание Middleware](tutorial/middleware/creating.md) — полный API, pipe-чейнинг
- [Примеры Middleware](tutorial/middleware/examples.md) — готовые рецепты
- [Справочник Middleware](reference/middleware.md) — документация по классам
- [Зависимости](dependencies.md) — для конкретных запросов

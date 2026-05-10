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

## Сессии / Персистентность кук

FastHTTP поддерживает автоматическую работу с куками через параметр `cookie_jar` — без лишних импортов middleware.

```python
from fasthttp import FastHTTP, CookieJar

app = FastHTTP(cookie_jar=CookieJar())
```

Куки из заголовков `Set-Cookie` автоматически сохраняются в jar и подставляются во все последующие запросы — в том числе между отдельными вызовами `app.run()`.

### Login flow (последовательные запросы через tags)

Все маршруты внутри одного `run()` выполняются параллельно, поэтому
для цепочки запросов, где каждый следующий зависит от куки предыдущего,
используй `tags`:

```python
from fasthttp import FastHTTP, CookieJar
from fasthttp.response import Response

app = FastHTTP(cookie_jar=CookieJar())


@app.post(
    url="https://api.example.com/login",
    json={"username": "alice", "password": "secret"},
    tags=["auth"],
)
async def login(resp: Response) -> dict:
    return resp.json()


@app.get(url="https://api.example.com/profile", tags=["protected"])
async def profile(resp: Response) -> dict:
    return resp.json()


app.run(tags=["auth"])       # login — куки сохраняются в jar
app.run(tags=["protected"])  # profile — Cookie-заголовок подставляется автоматически
```

### Предзагрузка кук

Передай начальный словарь кук чтобы пропустить шаг логина:

```python
app = FastHTTP(cookie_jar=CookieJar({"auth_token": "already-have-this"}))
```

### Просмотр и очистка кук

```python
jar = CookieJar()
app = FastHTTP(cookie_jar=jar)

# посмотреть что хранится
print(jar.get("session_id"))
print(jar.items())

# удалить все куки (например, logout)
jar.clear()
```

### Куки для IP / localhost

По умолчанию куки для не-доменных хостов отклоняются. Для локальной разработки используй `unsafe=True`:

```python
app = FastHTTP(cookie_jar=CookieJar(unsafe=True))
```

### Полностью отключить куки

Используй `DummyCookieJar` чтобы явно выключить обработку кук:

```python
from fasthttp import FastHTTP, DummyCookieJar

app = FastHTTP(cookie_jar=DummyCookieJar())
```

### Продвинутый вариант: SessionMiddleware напрямую

Для контроля приоритета или цепочки с другим middleware используй `SessionMiddleware` напрямую:

```python
from fasthttp import FastHTTP, SessionMiddleware, CacheMiddleware

app = FastHTTP(
    middleware=SessionMiddleware() | CacheMiddleware(ttl=60)
)
```

!!! note "Параллельные запросы и состояние сессии"
    Внутри одного вызова `app.run()` все маршруты запускаются одновременно
    через `asyncio.gather`. Если запрос B нуждается в куке, которую устанавливает
    запрос A, разбей их на отдельные `app.run(tags=[...])` — так A завершится
    до начала B.

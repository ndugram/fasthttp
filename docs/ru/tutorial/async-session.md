# AsyncSession

`AsyncSession` — это императивный HTTP-клиент для FastHTTP, аналог `httpx.AsyncClient`. Вместо того чтобы определять запросы через декораторы и вызывать `app.run()`, вы вызываете методы напрямую и сразу получаете ответ.

## Когда использовать AsyncSession vs FastHTTP

| | `FastHTTP` | `AsyncSession` |
|---|---|---|
| Стиль | Декларативный (декораторы) | Императивный (прямые вызовы) |
| Выполнение | Всё сразу через `app.run()` | По одному запросу |
| Результат | Логируется | Возвращается напрямую |
| Когда | Пакетные запросы, скрипты | Динамическая логика, циклы, условия |

Используйте `AsyncSession` когда нужно:
- Делать запросы внутри циклов или условий
- Сразу использовать результат для следующего шага
- Строить сложные цепочки запросов (например: логин → получить токен → использовать токен)

## Базовое использование

`AsyncSession` работает как async context manager:

```python
import asyncio
from fasthttp import AsyncSession


async def main():
    async with AsyncSession(base_url="https://jsonplaceholder.typicode.com") as session:
        resp = await session.get("/todos/1")
        if resp:
            print(resp.json())


asyncio.run(main())
```

## HTTP методы

Доступны все стандартные методы:

```python
import asyncio
from fasthttp import AsyncSession


async def main():
    async with AsyncSession(base_url="https://jsonplaceholder.typicode.com") as session:
        # GET
        resp = await session.get("/posts/1")

        # GET с query параметрами
        resp = await session.get("/posts", params={"userId": 1})

        # POST с JSON телом
        resp = await session.post("/posts", json={"title": "hello", "userId": 1})

        # PUT
        resp = await session.put("/posts/1", json={"id": 1, "title": "updated", "userId": 1})

        # PATCH
        resp = await session.patch("/posts/1", json={"title": "patched"})

        # DELETE
        resp = await session.delete("/posts/1")

        # HEAD
        resp = await session.head("/posts")

        # OPTIONS
        resp = await session.options("/posts")

        # Универсальный метод
        resp = await session.request("GET", "/posts/1")


asyncio.run(main())
```

## Параметры конструктора

```python
AsyncSession(
    base_url: str = None,
    headers: dict = None,
    timeout: float = 30.0,
    http2: bool = False,
    proxy: str = None,
    security: bool = True,
    middleware: list = None,
    cookie_jar: CookieJar = None,
    debug: bool = False,
    secret_key: bytes = None,
)
```

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `base_url` | `str` | `None` | Базовый URL, добавляемый к относительным путям |
| `headers` | `dict` | `None` | Заголовки сессии, отправляются с каждым запросом |
| `timeout` | `float` | `30.0` | Таймаут по умолчанию в секундах |
| `http2` | `bool` | `False` | Включить HTTP/2 |
| `proxy` | `str` | `None` | URL прокси-сервера |
| `security` | `bool` | `True` | Включить встроенную защиту (SSRF, circuit breaker и др.) |
| `middleware` | `list` | `None` | Middleware для всех запросов |
| `cookie_jar` | `CookieJar` | `None` | Хранилище cookies |
| `debug` | `bool` | `False` | Подробное логирование |
| `secret_key` | `bytes` | `None` | Ключ для HMAC подписи запросов (генерируется автоматически) |

## Заголовки на уровне сессии

Заголовки, заданные в сессии, отправляются с каждым запросом:

```python
import asyncio
from fasthttp import AsyncSession


async def main():
    async with AsyncSession(
        base_url="https://api.example.com",
        headers={
            "Authorization": "Bearer my-token",
            "Accept": "application/json",
        },
    ) as session:
        resp = await session.get("/users")   # заголовок Authorization включён
        resp = await session.get("/posts")   # заголовок Authorization включён


asyncio.run(main())
```

## Заголовки и таймаут для отдельного запроса

Можно переопределить заголовки или таймаут для конкретного запроса:

```python
import asyncio
from fasthttp import AsyncSession


async def main():
    async with AsyncSession(base_url="https://api.example.com") as session:
        resp = await session.get(
            "/slow-endpoint",
            headers={"X-Custom": "value"},
            timeout=60.0,
        )


asyncio.run(main())
```

Заголовки запроса **мержатся** поверх заголовков сессии. Заголовки сессии не заменяются.

## Без context manager

Можно управлять пулом соединений вручную:

```python
import asyncio
from fasthttp import AsyncSession


async def main():
    session = AsyncSession(base_url="https://api.example.com")
    await session.open()

    try:
        resp = await session.get("/users/1")
        if resp:
            print(resp.json())
    finally:
        await session.close()


asyncio.run(main())
```

Всегда вызывайте `close()` по завершении — это освобождает пул соединений.

## Работа с ответами

`AsyncSession` возвращает объект `Response` или `None` при ошибке/статусе 4xx+:

```python
import asyncio
from fasthttp import AsyncSession


async def main():
    async with AsyncSession(security=False) as session:
        resp = await session.get("https://jsonplaceholder.typicode.com/posts/1")
        if resp:
            print(resp.status)      # 200
            print(resp.json())      # dict
            print(resp.text)        # строка
            print(resp.headers)     # dict заголовков ответа


asyncio.run(main())
```

## Динамическая логика запросов

Главная сила `AsyncSession` — использовать результат одного запроса для следующего:

```python
import asyncio
from fasthttp import AsyncSession


async def main():
    async with AsyncSession(base_url="https://api.example.com") as session:
        # Шаг 1: логин
        auth = await session.post("/auth/login", json={"user": "admin", "pass": "secret"})
        if not auth:
            return

        token = auth.json()["token"]

        # Шаг 2: использовать токен в следующем запросе
        resp = await session.get(
            "/protected/data",
            headers={"Authorization": f"Bearer {token}"},
        )
        if resp:
            print(resp.json())


asyncio.run(main())
```

## С Middleware

Весь middleware fasthttp работает с `AsyncSession`:

```python
import asyncio
from fasthttp import AsyncSession, CacheMiddleware


async def main():
    async with AsyncSession(
        base_url="https://api.example.com",
        middleware=CacheMiddleware(),
        security=False,
    ) as session:
        resp = await session.get("/data")


asyncio.run(main())
```

## С Cookie Jar

```python
import asyncio
from fasthttp import AsyncSession, CookieJar


async def main():
    async with AsyncSession(
        base_url="https://api.example.com",
        cookie_jar=CookieJar(),
    ) as session:
        await session.post("/login", json={"user": "admin"})
        # cookies из Set-Cookie сохраняются и отправляются автоматически
        resp = await session.get("/dashboard")


asyncio.run(main())
```

## Импорт

```python
from fasthttp import AsyncSession
# или
from fasthttp.session import AsyncSession
```

# Класс FastHTTP

Основной класс приложения.

## Конструктор

```python
from fasthttp import FastHTTP

app = FastHTTP(
    debug: bool = False,
    http2: bool = False,
    proxy: str = None,
    security: bool = True,
    lifespan: Callable = None,
    middleware: list = [],
    base_url: str = None,
    get_request: dict = {},
    query_request: dict = {},
    post_request: dict = {},
    put_request: dict = {},
    patch_request: dict = {},
    delete_request: dict = {},
    concurrency: int = None,
)
```

## Параметры

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `debug` | `bool` | `False` | Режим отладки |
| `http2` | `bool` | `False` | Использовать HTTP/2 |
| `proxy` | `str` | `None` | URL прокси |
| `security` | `bool` | `True` | Включить безопасность |
| `lifespan` | `Callable` | `None` | Обработчик запуска/завершения |
| `middleware` | `list` | `[]` | Список middleware |
| `base_url` | `str` | `None` | Базовый URL для декораторов и роутеров |
| `get_request` | `dict` | `{}` | Настройки GET |
| `query_request` | `dict` | `{}` | Настройки QUERY |
| `post_request` | `dict` | `{}` | Настройки POST |
| `put_request` | `dict` | `{}` | Настройки PUT |
| `patch_request` | `dict` | `{}` | Настройки PATCH |
| `delete_request` | `dict` | `{}` | Настройки DELETE |
| `concurrency` | `int \| None` | `None` | Макс. параллельных запросов при `run()`. `None` = без лимита |

**Использование base_url:**

```python
app = FastHTTP(base_url="https://api.example.com")

@app.get("/users")      # → https://api.example.com/users
@app.post("/users")     # → https://api.example.com/users

@app.get("https://other.com/api")  # → https://other.com/api (абсолютный URL)
```

## Методы

### run()

Выполнить все зарегистрированные запросы.

```python
app.run(tags: list = None)
```

### web_run()

Запустить с Swagger UI.

```python
app.web_run(host: str = "127.0.0.1", port: int = 8000, base_url: str = "")
```

- `base_url` - Необязательный префикс URL для документации, например `"/api"`

### include_router()

Подключить `Router` к приложению.

```python
app.include_router(
    router: Router,
    prefix: str = "",
    tags: list = None,
    dependencies: list = None,
    base_url: str = None,
)
```

- `router` - Экземпляр роутера
- `prefix` - Необязательный префикс перед prefix роутера
- `tags` - Необязательные теги, добавляемые перед тегами роутера
- `dependencies` - Необязательные зависимости, добавляемые перед зависимостями роутера
- `base_url` - Необязательный override для base_url дерева роутеров

### get(), post(), put(), patch(), delete()

Декораторы для HTTP методов.

### query()

Декоратор для QUERY-запросов. Безопасен и идемпотентен как GET, но принимает тело `json`/`data` (как POST).

```python
@app.query(
    url: str,
    json: dict = None,
    data: bytes = None,
    params: dict = None,
    tags: list = [],
    dependencies: list = [],
    response_model: type = None,
    request_model: type = None,
    responses: dict = None,
)
```

### graphql()

Декоратор для GraphQL.

### exception_handler()

Декоратор, регистрирующий хендлер для конкретного типа исключения, в стиле FastAPI. Возвращаемое значение хендлера заменяет результат route вместо того, чтобы запрос просто тихо падал.

```python
@app.exception_handler(
    exc_type: type[Exception],
)
```

**Параметры:**
- `exc_type` - класс исключения, для которого вызывается этот хендлер

**Сигнатура хендлера:** `async def handler(route, exc) -> Any`

**Пример:**

```python
from fasthttp.exceptions import FastHTTPTimeoutError

@app.exception_handler(FastHTTPTimeoutError)
async def handle_timeout(route, exc):
    return {"error": "timeout", "url": route.url}
```

Также доступен на `Router` через `@router.exception_handler(...)`. См. [Event Hooks](../middleware.md#event-hooks) для `on_request`, `on_response`, `on_error` и деталей диспетчеризации по MRO.

## AsyncSession

Императивный async HTTP-клиент — аналог `httpx.AsyncClient`. Возвращает ответы напрямую вместо логирования.

```python
from fasthttp import AsyncSession
```

### Конструктор

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

### Параметры

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `base_url` | `str` | `None` | Базовый URL для относительных путей |
| `headers` | `dict` | `None` | Заголовки сессии, отправляются с каждым запросом |
| `timeout` | `float` | `30.0` | Таймаут по умолчанию в секундах |
| `http2` | `bool` | `False` | Включить HTTP/2 |
| `proxy` | `str` | `None` | URL прокси-сервера |
| `security` | `bool` | `True` | Включить встроенную защиту |
| `middleware` | `list` | `None` | Middleware для всех запросов |
| `cookie_jar` | `CookieJar` | `None` | Хранилище cookies |
| `debug` | `bool` | `False` | Подробное логирование |
| `secret_key` | `bytes` | `None` | Ключ HMAC подписи (генерируется автоматически) |

### Методы

| Метод | Сигнатура |
|-------|-----------|
| `get` | `(url, *, params, headers, timeout) → Response \| None` |
| `query` | `(url, *, json, data, headers, timeout) → Response \| None` |
| `post` | `(url, *, json, data, headers, timeout) → Response \| None` |
| `put` | `(url, *, json, data, headers, timeout) → Response \| None` |
| `patch` | `(url, *, json, data, headers, timeout) → Response \| None` |
| `delete` | `(url, *, json, data, headers, timeout) → Response \| None` |
| `head` | `(url, *, params, headers, timeout) → Response \| None` |
| `options` | `(url, *, params, headers, timeout) → Response \| None` |
| `request` | `(method, url, *, params, json, data, headers, timeout) → Response \| None` |
| `open` | `() → None` — открыть пул соединений |
| `close` | `() → None` — закрыть пул соединений |

### Пример

```python
import asyncio
from fasthttp import AsyncSession


async def main():
    async with AsyncSession(
        base_url="https://api.example.com",
        headers={"Authorization": "Bearer token"},
    ) as session:
        resp = await session.get("/users")
        if resp:
            print(resp.json())


asyncio.run(main())
```

Полное руководство: [AsyncSession](../tutorial/async-session.md)

## Router

`Router` доступен через:

```python
from fasthttp import Router
```

Базовый конструктор:

```python
Router(
    base_url: str = None,
    prefix: str = "",
    tags: list = None,
    dependencies: list = None,
)
```

Примеры использования есть в:
- `docs/ru/tutorial/routers.md`

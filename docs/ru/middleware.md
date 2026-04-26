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

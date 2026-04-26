# Справочник Middleware

## BaseMiddleware

Базовый класс для всех middleware. Наследуйтесь и переопределяйте `request` и/или `response`.

```python
from fasthttp.middleware import BaseMiddleware

class MyMiddleware(BaseMiddleware):
    __return_type__ = None
    __priority__ = 0
    __methods__ = None
    __enabled__ = True

    async def request(self, method, url, kwargs):
        return kwargs

    async def response(self, response):
        return response

    async def on_error(self, error, route, config):
        pass
```

### Атрибуты класса

| Атрибут | Тип | Описание |
|---------|-----|----------|
| `__return_type__` | `type \| None` | Тип, с которым работает middleware |
| `__priority__` | `int` | Порядок выполнения (меньше = раньше) |
| `__methods__` | `list[str] \| None` | HTTP-методы для применения. `None` = все |
| `__enabled__` | `bool` | `False` пропускает без удаления из цепочки |

### Методы

#### `request(method, url, kwargs) → dict`

Вызывается до отправки запроса.

| Параметр | Тип | Описание |
|----------|-----|----------|
| `method` | `str` | HTTP-метод (`"GET"`, `"POST"` и т.д.) |
| `url` | `str` | Разрешённый URL |
| `kwargs` | `dict` | Аргументы запроса: `headers`, `params`, `json`, `data`, `timeout` |

**Возвращает:** модифицированный `kwargs`.

#### `response(response) → Response`

Вызывается после получения ответа. Вызывается в **обратном** порядке приоритетов.

| Параметр | Тип | Описание |
|----------|-----|----------|
| `response` | `Response` | Объект ответа |

**Возвращает:** модифицированный `Response`.

#### `on_error(error, route, config) → None`

Вызывается при ошибке запроса.

| Параметр | Тип | Описание |
|----------|-----|----------|
| `error` | `Exception` | Исключение |
| `route` | `Route` | Информация о маршруте |
| `config` | `dict` | Конфигурация запроса |

---

## MiddlewareChain

Упорядоченная цепочка middleware, создаётся через оператор `|`.

```python
from fasthttp.middleware import MiddlewareChain

chain = AuthMiddleware() | LoggingMiddleware() | TimingMiddleware()
```

Передаётся напрямую в `FastHTTP`:

```python
app = FastHTTP(middleware=chain)
```

### Методы

| Метод | Описание |
|-------|----------|
| `__or__(other)` | Добавляет middleware в конец цепочки |
| `__iter__()` | Итерация по middleware |
| `__len__()` | Количество middleware в цепочке |
| `__repr__()` | Строковое представление |

---

## MiddlewareManager

Внутренний менеджер, управляющий выполнением цепочки. Принимает `list`, `MiddlewareChain` или `None`.

```python
from fasthttp.middleware import MiddlewareManager

manager = MiddlewareManager([AuthMiddleware(), LoggingMiddleware()])
```

Методы вызываются автоматически из `HTTPClient`.

---

## CacheMiddleware

Встроенный middleware для кэширования ответов в памяти.

```python
from fasthttp import FastHTTP, CacheMiddleware

app = FastHTTP(
    middleware=[CacheMiddleware(ttl=3600, max_size=100)]
)
```

### Параметры конструктора

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `ttl` | `int` | `3600` | Время жизни кэша в секундах |
| `max_size` | `int` | `100` | Максимальное число записей (LRU-вытеснение) |
| `cache_methods` | `list[str]` | `["GET"]` | HTTP-методы для кэширования |

### Методы

| Метод | Описание |
|-------|----------|
| `clear()` | Очищает весь кэш |
| `get_stats()` | Возвращает статистику кэша |

```python
cache = CacheMiddleware(ttl=60)
app = FastHTTP(middleware=[cache])

# позже
cache.clear()
print(cache.get_stats())
# {'size': 0, 'max_size': 100, 'ttl': 60, 'methods': ['GET']}
```

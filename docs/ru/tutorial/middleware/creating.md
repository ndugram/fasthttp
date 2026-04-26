# Создание Middleware

## BaseMiddleware

Все middleware наследуются от `BaseMiddleware`:

```python
from fasthttp.middleware import BaseMiddleware

class MyMiddleware(BaseMiddleware):
    __return_type__ = bool
    __priority__ = 0
    __methods__ = None
    __enabled__ = True

    async def request(self, method, url, kwargs):
        # модифицируем kwargs до отправки запроса
        return kwargs

    async def response(self, response):
        # инспектируем или модифицируем ответ
        return response

    async def on_error(self, error, route, config):
        # обрабатываем ошибку
        pass
```

## Атрибуты класса

| Атрибут | Тип | Описание |
|---------|-----|----------|
| `__return_type__` | `type \| None` | Тип, с которым работает middleware |
| `__priority__` | `int` | Порядок выполнения — **меньше = раньше** |
| `__methods__` | `list[str] \| None` | HTTP-методы для перехвата. `None` = все методы |
| `__enabled__` | `bool` | `False` пропускает middleware без удаления из цепочки |

!!! note "Нет значений по умолчанию"
    Ни один из этих атрибутов не имеет дефолта в `BaseMiddleware`. Определяйте
    только те, которые нужны.

## `request(method, url, kwargs)`

Вызывается **до** отправки HTTP-запроса. Получает:

- `method` — HTTP-метод (`"GET"`, `"POST"` и т.д.)
- `url` — разрешённый URL (схема уже добавлена)
- `kwargs` — dict с ключами: `params`, `headers`, `json`, `data`, `timeout`

Должен вернуть (возможно изменённый) dict `kwargs`:

```python
async def request(self, method, url, kwargs):
    kwargs["headers"] = kwargs.get("headers") or {}
    kwargs["headers"]["X-Request-ID"] = "some-id"
    return kwargs
```

!!! warning "headers может быть None"
    `kwargs["headers"]` равен `None`, когда заголовки не передавались.
    Всегда используйте `kwargs.get("headers") or {}` перед добавлением ключей.

## `response(response)`

Вызывается **после** получения HTTP-ответа. Получает объект `Response`.
Должен вернуть `Response`:

```python
async def response(self, response):
    if response.status >= 400:
        print(f"Ошибка {response.status}")
    return response
```

## `on_error(error, route, config)`

Вызывается при **ошибке запроса**. Получает:

- `error` — исключение
- `route` — информация о маршруте
- `config` — конфигурация запроса

```python
async def on_error(self, error, route, config):
    print(f"Ошибка: {route.method} {route.url} — {error}")
```

## Dunder-методы

### `__repr__`

```python
mw = MyMiddleware()
print(mw)   # <MyMiddleware return_type=<class 'bool'>>
```

### `__or__` — pipe-чейнинг

Объединяйте middleware через `|`:

```python
chain = AuthMiddleware() | LoggingMiddleware() | TimingMiddleware()
```

Результат — `MiddlewareChain`, передаётся прямо в `FastHTTP`:

```python
app = FastHTTP(middleware=chain)
```

### `__init_subclass__`

Срабатывает при наследовании от `BaseMiddleware`. Переопределите для валидации подклассов:

```python
class StrictMiddleware(BaseMiddleware):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "__priority__"):
            raise TypeError(f"{cls.__name__} должен определить __priority__")
```

## Подключение к приложению

=== "Список"

    ```python
    FastHTTP(middleware=[AuthMiddleware(), LoggingMiddleware()])
    ```

=== "Pipe"

    ```python
    FastHTTP(middleware=AuthMiddleware() | LoggingMiddleware())
    ```

=== "Один"

    ```python
    FastHTTP(middleware=AuthMiddleware())
    ```

Все три варианта эквивалентны. Порядок сортировки определяется `__priority__` автоматически.

## Toggle в рантайме

```python
debug = LoggingMiddleware()
app = FastHTTP(middleware=[debug])

# отключить без удаления из цепочки
debug.__enabled__ = False

# включить обратно
debug.__enabled__ = True
```

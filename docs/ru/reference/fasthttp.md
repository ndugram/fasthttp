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
    post_request: dict = {},
    put_request: dict = {},
    patch_request: dict = {},
    delete_request: dict = {},
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
| `post_request` | `dict` | `{}` | Настройки POST |
| `put_request` | `dict` | `{}` | Настройки PUT |
| `patch_request` | `dict` | `{}` | Настройки PATCH |
| `delete_request` | `dict` | `{}` | Настройки DELETE |

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

### graphql()

Декоратор для GraphQL.

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

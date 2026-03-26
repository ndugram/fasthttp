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
| `get_request` | `dict` | `{}` | Настройки GET |

## Методы

### run()

Выполнить все зарегистрированные запросы.

```python
app.run(tags: list = None)
```

### web_run()

Запустить с Swagger UI.

```python
app.web_run(host: str = "127.0.0.1", port: int = 8000)
```

### get(), post(), put(), patch(), delete()

Декораторы для HTTP методов.

### graphql()

Декоратор для GraphQL.

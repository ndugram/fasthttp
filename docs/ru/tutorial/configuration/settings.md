# Настройки

Основная конфигурация приложения.

## Параметры конструктора

```python
from fasthttp import FastHTTP

app = FastHTTP(
    debug=False,      # Режим отладки
    http2=False,      # Использовать HTTP/2
    proxy=None,       # Прокси сервер
    security=True,    # Включить безопасность
    lifespan=None,    # Обработчик запуска/завершения
    middleware=[],    # Список middleware
    get_request={},   # Настройки по умолчанию для GET
    post_request={},  # Настройки по умолчанию для POST
    put_request={},   # Настройки по умолчанию для PUT
    patch_request={}, # Настройки по умолчанию для PATCH
    delete_request={} # Настройки по умолчанию для DELETE
)
```

## Таблица параметров

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `debug` | `bool` | `False` | Включить режим отладки |
| `http2` | `bool` | `False` | Использовать HTTP/2 |
| `proxy` | `str` | `None` | URL прокси сервера |
| `security` | `bool` | `True` | Включить функции безопасности |
| `lifespan` | `Callable` | `None` | Обработчик запуска/завершения |
| `middleware` | `list` | `[]` | Список middleware |
| `get_request` | `dict` | `{}` | Настройки GET |
| `post_request` | `dict` | `{}` | Настройки POST |

## Минимальная конфигурация

```python
from fasthttp import FastHTTP

app = FastHTTP()
```

## Полная конфигурация

```python
app = FastHTTP(
    debug=True,
    http2=False,
    proxy="http://proxy.example.com:8080",
    security=True,
    middleware=[MyMiddleware()],
    get_request={
        "headers": {"User-Agent": "MyApp/1.0"},
        "timeout": 30.0,
    },
    post_request={
        "headers": {"Content-Type": "application/json"},
        "timeout": 60.0,
    },
)
```

## Настройки по методу

Каждый HTTP метод может иметь свои настройки по умолчанию:

```python
app = FastHTTP(
    get_request={"timeout": 30.0},
    post_request={"timeout": 60.0},
    put_request={"timeout": 60.0},
    delete_request={"timeout": 30.0},
)
```

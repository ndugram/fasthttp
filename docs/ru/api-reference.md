# API

Полный справочник по FastHTTP.

## FastHTTP

Основной класс для HTTP запросов.

```python
from fasthttp import FastHTTP

app = FastHTTP(
    debug=False,
    http2=False,
    middleware=None,
)
```

### Параметры конструктора

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `debug` | `bool` | `False` | Подробное логирование |
| `http2` | `bool` | `False` | Использовать HTTP/2 |
| `middleware` | `BaseMiddleware` / `list` | `None` | Middleware |
| `get_request` | `dict` | `None` | Конфигурация GET |
| `post_request` | `dict` | `None` | Конфигурация POST |
| `put_request` | `dict` | `None` | Конфигурация PUT |
| `patch_request` | `dict` | `None` | Конфигурация PATCH |
| `delete_request` | `dict` | `None` | Конфигурация DELETE |

### Методы

#### `.get(url, params, response_model)`

```python
@app.get(url="https://api.example.com/users", params={"page": 1})
async def get_users(resp):
    return resp.json()
```

#### `.post(url, json, data, params, response_model)`

```python
@app.post(url="https://api.example.com/users", json={"name": "John"})
async def create_user(resp):
    return resp.status
```

#### `.put()` / `.patch()` / `.delete()` — аналогично `.post()`

#### `.run()`

Выполнить все запросы:

```python
if __name__ == "__main__":
    app.run()
```

## Response

HTTP ответ.

### Атрибуты

| Атрибут | Тип | Описание |
|---------|-----|----------|
| `status` | `int` | Код статуса (200, 404 и т.д.) |
| `text` | `str` | Тело ответа |
| `headers` | `dict` | Заголовки ответа |

### Методы

#### `.json()`

Распарсить JSON:

```python
data = resp.json()
```

Вызывает `json.JSONDecodeError` при ошибке.

## Конфигурация запроса

```python
{
    "headers": {"User-Agent": "MyApp/1.0"},
    "timeout": 30,
    "allow_redirects": True,
}
```

### Опции

| Опция | Тип | По умолчанию | Описание |
|-------|-----|--------------|----------|
| `headers` | `dict` | `{}` | Заголовки |
| `timeout` | `int` | `30` | Таймаут (сек) |
| `allow_redirects` | `bool` | `True` | Следовать редиректам |

## Middleware

Перехват и модификация запросов/ответов.

```python
from fasthttp.middleware import BaseMiddleware


class MyMiddleware(BaseMiddleware):
    async def before_request(self, route, config):
        # Изменить конфиг до запроса
        return config

    async def after_response(self, response, route, config):
        # Изменить ответ после запроса
        return response

    async def on_error(self, error, route, config):
        # Обработать ошибку
        pass
```

```python
app = FastHTTP(middleware=MyMiddleware())
```

## Ошибки

Автоматически перехватываются и логируются:

- `FastHTTPConnectionError` — ошибка подключения
- `FastHTTPTimeoutError` — таймаут
- `FastHTTPBadStatusError` — HTTP 4xx/5xx

Вызвать вручную:

```python
from fasthttp.exceptions import FastHTTPBadStatusError

raise FastHTTPBadStatusError("Not found", url=url, status_code=404)
```

## Логирование

```python
app = FastHTTP(debug=True)
```

По умолчанию показывает статус и время:

```
✔ GET https://api.example.com [200] 234.56ms
```

Debug mode показывает заголовки, тело, тайминг.

## Производительность

Все запросы выполняются параллельно. Небольшая задержка (0.5с) между запросами.

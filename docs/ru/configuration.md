# Конфигурация

Подробное руководство по настройке FastHTTP.

## Базовая конфигурация

При создании приложения можно передать глобальные настройки:

```python
from fasthttp import FastHTTP

app = FastHTTP(
    debug=False,  # Режим отладки
    http2=False,  # Использовать HTTP/2
    get_request={
        "headers": {"User-Agent": "MyApp/1.0"},
        "timeout": 30.0,
        "allow_redirects": True,
    },
    post_request={
        "headers": {"Content-Type": "application/json"},
        "timeout": 30.0,
        "allow_redirects": True,
    },
)
```

## Параметры конфигурации

### Параметры приложения

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `debug` | `bool` | `False` | Включить подробное логирование |
| `http2` | `bool` | `False` | Использовать HTTP/2 |
| `get_request` | `dict` | `{}` | Настройки по умолчанию для GET |
| `post_request` | `dict` | `{}` | Настройки по умолчанию для POST |
| `put_request` | `dict` | `{}` | Настройки по умолчанию для PUT |
| `patch_request` | `dict` | `{}` | Настройки по умолчанию для PATCH |
| `delete_request` | `dict` | `{}` | Настройки по умолчанию для DELETE |

### Параметры запроса

Каждый метод HTTP может иметь свои настройки по умолчанию:

```python
app = FastHTTP(
    get_request={
        "headers": {
            "User-Agent": "MyApp/1.0",
            "Accept": "application/json",
        },
        "timeout": 30.0,
        "allow_redirects": True,
    },
    post_request={
        "headers": {
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        "timeout": 60.0,  # POST может быть дольше
        "allow_redirects": False,
    },
)
```

## Переопределение настроек

Настройки можно переопределять для конкретных запросов:

```python
# Глобальный таймаут 30 секунд
app = FastHTTP(get_request={"timeout": 30.0})


# Переопределяем для конкретного запроса
@app.get(url="https://api.example.com/fast", timeout=5.0)
async def fast_request(resp):
    return resp.json()


@app.get(url="https://api.example.com/slow", timeout=120.0)
async def slow_request(resp):
    return resp.json()
```

## Заголовки

### Основные типы заголовков

```python
from fasthttp import FastHTTP

app = FastHTTP()


# Bearer токен (наиболее распространённый)
app = FastHTTP(
    get_request={
        "headers": {"Authorization": "Bearer your-token-here"}
    }
)


# API ключ (альтернативный способ)
app = FastHTTP(
    get_request={
        "headers": {"X-API-Key": "your-api-key"}
    }
)


# Basic Authentication
import base64

app = FastHTTP(
    get_request={
        "headers": {
            "Authorization": f"Basic {base64.b64encode(b'username:password').decode()}"
        }
    }
)


# Custom User-Agent
app = FastHTTP(
    get_request={
        "headers": {"User-Agent": "MyApp/1.0 (https://myapp.com)"}
    }
)
```

### Динамические заголовки

Для динамических заголовков используйте зависимости:

```python
from fasthttp import FastHTTP, Depends

app = FastHTTP()


async def add_auth(route, config):
    import os
    token = os.getenv("API_TOKEN")
    config.setdefault("headers", {})["Authorization"] = f"Bearer {token}"
    return config


@app.get(
    url="https://api.example.com/data",
    dependencies=[Depends(add_auth)]
)
async def handler(resp):
    return resp.json()
```

## Таймаут

Таймаут задаётся в секундах:

```python
# Глобальный таймаут
app = FastHTTP(get_request={"timeout": 30.0})


# Локальный таймаут
@app.get(url="https://api.example.com/data", timeout=10.0)
async def handler(resp):
    return resp.json()
```

### Рекомендации по таймаутам

- GET запросы: 10-30 секунд
- POST/PUT запросы: 30-60 секунд
- Загрузка файлов: 120+ секунд

## Логирование

### Режим отладки

```python
# Подробный вывод (все заголовки, тело, время)
app = FastHTTP(debug=True)


# Минимальный вывод (только статус и время)
app = FastHTTP(debug=False)
```

При `debug=True` выводится:

```
DEBUG   │ fasthttp    │ 🐛 → GET https://api.example.com/data | headers={'User-Agent': 'fasthttp/0.1.0'}
DEBUG   │ fasthttp    │ 🐛 ← 200 | headers={'Content-Type': 'application/json'}
INFO    │ fasthttp    │ ✔ ✔ GET https://api.example.com/data 200 150.23ms
```

При `debug=False`:

```
INFO    │ fasthttp    │ ✔ ✔ GET https://api.example.com/data 200 150.23ms
```

## Переменные окружения

Используйте переменные окружения для конфигурации:

```python
import os
from fasthttp import FastHTTP

app = FastHTTP(
    debug=os.getenv("DEBUG", "false").lower() == "true",
    http2=os.getenv("HTTP2", "false").lower() == "true",
    get_request={
        "headers": {
            "Authorization": f"Bearer {os.getenv('API_TOKEN')}",
            "User-Agent": os.getenv("USER_AGENT", "MyApp/1.0"),
        },
        "timeout": float(os.getenv("TIMEOUT", "30.0")),
    },
)
```

### Пример .env файла

```bash
# .env
DEBUG=true
HTTP2=false
API_TOKEN=your-secret-token
USER_AGENT=MyApp/1.0
TIMEOUT=30.0
```

## HTTP/2

Включите HTTP/2 для улучшенной производительности:

```python
app = FastHTTP(http2=True)
```

Требования:

```bash
pip install fasthttp-client[http2]
```

Подробнее в разделе [HTTP/2](http2-support.md).

## Конфигурация по методу HTTP

Можно настраивать разные параметры для разных HTTP методов:

```python
app = FastHTTP(
    # Настройки для GET
    get_request={
        "headers": {
            "Accept": "application/json",
            "User-Agent": "MyApp/1.0",
        },
        "timeout": 30.0,
    },
    
    # Настройки для POST
    post_request={
        "headers": {
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        "timeout": 60.0,
    },
    
    # Настройки для PUT
    put_request={
        "headers": {
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        "timeout": 60.0,
    },
    
    # Настройки для DELETE
    delete_request={
        "headers": {
            "Accept": "application/json",
        },
        "timeout": 30.0,
    },
)
```

## Примеры конфигурации

### Минимальная конфигурация

```python
from fasthttp import FastHTTP

app = FastHTTP()
```

### Конфигурация для API

```python
import os
from fasthttp import FastHTTP

app = FastHTTP(
    debug=os.getenv("DEBUG", "false").lower() == "true",
    get_request={
        "headers": {
            "Authorization": f"Bearer {os.getenv('API_TOKEN')}",
            "User-Agent": "MyApp/1.0",
            "Accept": "application/json",
        },
        "timeout": 30.0,
    },
    post_request={
        "headers": {
            "Authorization": f"Bearer {os.getenv('API_TOKEN')}",
            "Content-Type": "application/json",
            "User-Agent": "MyApp/1.0",
        },
        "timeout": 60.0,
    },
)
```

### Конфигурация для разработки

```python
from fasthttp import FastHTTP

app = FastHTTP(
    debug=True,  # Подробное логирование
    get_request={
        "headers": {
            "User-Agent": "DevApp/1.0",
        },
        "timeout": 300.0,  # Длинный таймаут для отладки
    },
)
```

## Смотрите также

- [Быстрый старт](quick-start.md) — основы
- [HTTP/2](http2-support.md) — поддержка HTTP/2
- [Зависимости](dependencies.md) — модификация запросов
- [CLI](cli.md) — командная строка

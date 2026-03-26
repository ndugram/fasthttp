# Переменные окружения

Настройка FastHTTP с использованием переменных окружения.

## Базовое использование

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

## Файл .env

```bash
DEBUG=true
HTTP2=false
API_TOKEN=your-secret-token
USER_AGENT=MyApp/1.0
TIMEOUT=30.0
```

## Таблица переменных

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `DEBUG` | `false` | Включить режим отладки |
| `HTTP2` | `false` | Включить HTTP/2 |
| `API_TOKEN` | - | Токен API |
| `USER_AGENT` | `fasthttp` | Заголовок User-Agent |
| `TIMEOUT` | `30.0` | Таймаут запроса |
| `PROXY` | - | URL прокси сервера |

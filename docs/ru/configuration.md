# Конфигурация

Настройка FastHTTP.

## Базовая

```python
app = FastHTTP(
    debug=False,
    get_request={
        "headers": {"User-Agent": "MyApp/1.0"},
        "timeout": 30,
    },
    post_request={
        "headers": {"Content-Type": "application/json"},
        "timeout": 30,
    },
)
```

## Переопределение

```python
@app.get(url="https://api.example.com/data", params={"page": 1})
async def get_data(resp):
    return resp.json()
```

## Заголовки

```python
# Bearer токен
{"Authorization": "Bearer token"}

# API ключ
{"X-API-Key": "key"}

# Basic auth
import base64
{"Authorization": f"Basic {base64.b64encode(b'user:pass').decode()}"}
```

## Переменные окружения

```python
import os

app = FastHTTP(
    debug=os.getenv("DEBUG", "false").lower() == "true",
    get_request={
        "headers": {"Authorization": f"Bearer {os.getenv('API_KEY')}"},
        "timeout": int(os.getenv("TIMEOUT", "30")),
    },
)
```

## Таймаут

```python
app = FastHTTP(get_request={"timeout": 30})
```

## Логирование

```python
app = FastHTTP(debug=True)  # Показывает заголовки, тело, время
```

По умолчанию показывает только статус и время.

## HTTP/2

```python
app = FastHTTP(http2=True)
```

Требует: `pip install fasthttp-client[http2]`

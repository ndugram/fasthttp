# Заголовки

Настройка HTTP заголовков для запросов.

## Глобальные заголовки

```python
app = FastHTTP(
    get_request={
        "headers": {
            "Authorization": "Bearer your-token-here",
            "User-Agent": "MyApp/1.0",
            "Accept": "application/json",
        }
    }
)
```

## Локальные заголовки

```python
@app.get(
    url="https://api.example.com/data",
    get_request={"headers": {"X-Custom-Header": "value"}}
)
async def handler(resp):
    return resp.json()
```

## Типичные заголовки

### Bearer токен

```python
app = FastHTTP(
    get_request={"headers": {"Authorization": "Bearer your-token-here"}}
)
```

### API ключ

```python
app = FastHTTP(
    get_request={"headers": {"X-API-Key": "your-api-key"}}
)
```

## Динамические заголовки

Для динамических заголовков используйте зависимости:

```python
from fasthttp import FastHTTP, Depends
import os


async def add_auth(route, config):
    token = os.getenv("API_TOKEN")
    config.setdefault("headers", {})["Authorization"] = f"Bearer {token}"
    return config
```

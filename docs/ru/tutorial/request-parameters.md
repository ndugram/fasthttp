# Параметры запроса

Узнайте, как передавать различные типы данных в запросах.

## Query параметры

Используйте параметр `params`:

```python
@app.get(
    url="https://api.example.com/search",
    params={"q": "fasthttp", "page": 1, "limit": 10}
)
async def search(resp: Response) -> dict:
    return resp.json()

# Фактический URL: https://api.example.com/search?q=fasthttp&page=1&limit=10
```

## JSON тело

Используйте параметр `json`:

```python
@app.post(
    url="https://api.example.com/users",
    json={"name": "John", "email": "john@example.com", "age": 25}
)
async def create_user(resp: Response) -> dict:
    return resp.json()
```

## Raw данные

Используйте параметр `data`:

```python
@app.post(
    url="https://api.example.com/upload",
    data=b"raw bytes data"
)
async def upload(resp: Response) -> dict:
    return resp.json()
```

## Заголовки

### Глобальные заголовки

```python
app = FastHTTP(
    get_request={
        "headers": {
            "Authorization": "Bearer my-secret-token",
            "User-Agent": "MyApp/1.0",
            "Accept": "application/json",
        }
    }
)
```

### Локальные заголовки

```python
@app.get(
    url="https://api.example.com/data",
    get_request={
        "headers": {"X-Custom-Header": "value"}
    }
)
async def with_headers(resp: Response) -> dict:
    return resp.json()
```

## Таймаут

Переопределите таймаут для отдельного запроса:

```python
@app.get(
    url="https://api.example.com/slow",
    timeout=120.0
)
async def slow_request(resp: Response) -> dict:
    return resp.json()
```

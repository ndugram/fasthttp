# Lifespan

Lifespan позволяет выполнять код до и после всех запросов.

## Базовое использование

```python
from contextlib import asynccontextmanager
from fasthttp import FastHTTP
from fasthttp.response import Response


@asynccontextmanager
async def lifespan(app: FastHTTP):
    # Запуск - выполняется перед запросами
    print("Starting up...")
    app.auth_token = "my-secret-token"

    yield  # Здесь выполняются запросы

    # Завершение - выполняется после запросов
    print("Shutting down...")


app = FastHTTP(lifespan=lifespan)


@app.get(url="https://api.example.com/data")
async def get_data(resp: Response) -> dict:
    return resp.json()


app.run()
```

Вывод:

```
Starting up...
INFO    | fasthttp    | FastHTTP started
INFO    | fasthttp    | Sending 1 requests
INFO    | fasthttp    | GET https://api.example.com/data 200 150ms
INFO    | fasthttp    | Done in 0.15s
Shutting down...
```

## Варианты использования

### Загрузка конфигурации

```python
import os
import json


@asynccontextmanager
async def lifespan(app: FastHTTP):
    with open("config.json") as f:
        app.config = json.load(f)
    
    yield


app = FastHTTP(lifespan=lifespan)
```

### Подключение к сервисам

```python
import aioredis


@asynccontextmanager
async def lifespan(app: FastHTTP):
    app.redis = await aioredis.from_url("redis://localhost")
    print("Redis connected")

    yield

    await app.redis.close()
    print("Redis disconnected")


app = FastHTTP(lifespan=lifespan)
```

### Загрузка токенов

```python
@asynccontextmanager
async def lifespan(app: FastHTTP):
    app.api_token = os.getenv("API_TOKEN")
    yield


app = FastHTTP(lifespan=lifespan)
```

### Сбор статистики

```python
@asynccontextmanager
async def lifespan(app: FastHTTP):
    app.request_count = 0
    app.total_time = 0.0

    yield

    print(f"Total requests: {app.request_count}")
    print(f"Total time: {app.total_time:.2f}s")


app = FastHTTP(lifespan=lifespan)
```

## Без Lifespan

Если `lifespan` не указан, приложение работает обычным образом:

```python
app = FastHTTP()  # Без lifespan


@app.get(url="https://api.example.com/data")
async def get_data(resp: Response) -> dict:
    return resp.json()


app.run()
```

## Использование атрибутов приложения

Вы можете добавлять собственные атрибуты к приложению и обращаться к ним в обработчиках:

```python
@asynccontextmanager
async def lifespan(app: FastHTTP):
    app.base_url = "https://api.example.com"
    app.api_key = "secret-key"
    yield


app = FastHTTP(lifespan=lifespan)


@app.get(url="https://api.example.com/data")
async def get_data(resp: Response) -> dict:
    headers = {"X-API-Key": app.api_key}
    return resp.json()
```

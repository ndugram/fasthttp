# Примеры

Практические примеры использования FastHTTP.

## Базовые примеры

### Простой GET запрос

```python
from fasthttp import FastHTTP

app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def main(resp):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

### POST запрос с JSON

```python
from fasthttp import FastHTTP

app = FastHTTP()


@app.post(
    url="https://jsonplaceholder.typicode.com/posts",
    json={
        "title": "My Post",
        "body": "Content here",
        "userId": 1,
    }
)
async def create_post(resp):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

### Несколько запросов параллельно

```python
from fasthttp import FastHTTP

app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def get_post(resp):
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/users/1")
async def get_user(resp):
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/comments/1")
async def get_comment(resp):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

## Заголовки и аутентификация

### Bearer токен

```python
from fasthttp import FastHTTP

app = FastHTTP(
    get_request={
        "headers": {
            "Authorization": "Bearer your-token-here",
        }
    }
)


@app.get(url="https://api.example.com/protected")
async def protected(resp):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

### API ключ

```python
from fasthttp import FastHTTP

app = FastHTTP(
    get_request={
        "headers": {
            "X-API-Key": "your-api-key",
        }
    }
)


@app.get(url="https://api.example.com/data")
async def with_api_key(resp):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

## Теги

### Группировка запросов

```python
from fasthttp import FastHTTP

app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/users", tags=["users"])
async def get_users(resp):
    return resp.json()


@app.post(url="https://jsonplaceholder.typicode.com/users", tags=["users"])
async def create_user(resp):
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/posts", tags=["posts"])
async def get_posts(resp):
    return resp.json()


@app.post(url="https://jsonplaceholder.typicode.com/posts", tags=["posts"])
async def create_post(resp):
    return resp.json()


# Запустить только пользователей
if __name__ == "__main__":
    app.run(tags=["users"])
```

## Зависимости

### Добавление заголовков

```python
from fasthttp import FastHTTP, Depends
from fasthttp.response import Response

app = FastHTTP()


async def add_auth(route, config):
    config.setdefault("headers", {})["Authorization"] = "Bearer token"
    return config


async def add_trace_id(route, config):
    import uuid
    config.setdefault("headers", {})["X-Trace-ID"] = str(uuid.uuid4())
    return config


@app.get(
    url="https://httpbin.org/headers",
    dependencies=[Depends(add_auth), Depends(add_trace_id)]
)
async def with_dependencies(resp: Response):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

## Middleware

### Логирование

```python
import time
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware

app = FastHTTP()


class LoggingMiddleware(BaseMiddleware):
    async def before_request(self, route, config):
        print(f"🚀 {route.method} {route.url}")
        config["_start_time"] = time.time()
        return config

    async def after_response(self, response, route, config):
        duration = time.time() - config.get("_start_time", 0)
        print(f"✅ {route.method} {route.url} - {response.status} ({duration:.2f}s)")
        return response


app = FastHTTP(middleware=[LoggingMiddleware()])


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def main(resp):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

### Кеширование

```python
from fasthttp import FastHTTP, CacheMiddleware

app = FastHTTP(middleware=[CacheMiddleware(ttl=3600)])


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def cached_request(resp):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

## Pydantic валидация

### Простая модель

```python
from pydantic import BaseModel
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


class User(BaseModel):
    id: int
    name: str
    email: str


@app.get(
    url="https://jsonplaceholder.typicode.com/users/1",
    response_model=User
)
async def get_user(resp: Response):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

### Вложенные модели

```python
from pydantic import BaseModel
from typing import List
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


class Geo(BaseModel):
    lat: str
    lng: str


class Address(BaseModel):
    street: str
    suite: str
    city: str
    zipcode: str
    geo: Geo


class User(BaseModel):
    id: int
    name: str
    email: str
    address: Address


@app.get(
    url="https://jsonplaceholder.typicode.com/users/1",
    response_model=User
)
async def get_user(resp: Response):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

## Обработка ошибок

### Обработка статусов

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)


@app.get(url="https://httpbin.org/status/404")
async def not_found(resp: Response):
    return {"error": "Not found", "status": resp.status}


@app.get(url="https://httpbin.org/status/500")
async def server_error(resp: Response):
    return {"error": "Server error", "status": resp.status}


if __name__ == "__main__":
    app.run()
```

## Конфигурация

### Полная конфигурация

```python
import os
from fasthttp import FastHTTP

app = FastHTTP(
    debug=os.getenv("DEBUG", "false").lower() == "true",
    http2=False,
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
        "timeout": 60.0,
    },
)


@app.get(url="https://api.example.com/data")
async def get_data(resp):
    return resp.json()


@app.post(url="https://api.example.com/data")
async def post_data(resp):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

## Смотрите также

- [Быстрый старт](quick-start.md) — основы
- [CLI](cli.md) — командная строка
- [Конфигурация](configuration.md) — настройки

# Примеры

Практические примеры.

## Базовый GET

```python
from fasthttp import FastHTTP

app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def get_post(resp):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

## POST JSON

```python
@app.post(url="https://jsonplaceholder.typicode.com/posts", json={
    "title": "FastHTTP",
    "body": "Контент",
    "userId": 1
})
async def create_post(resp):
    return resp.json()
```

## Параметры запроса

```python
@app.get(url="https://jsonplaceholder.typicode.com/posts", params={"userId": 1})
async def get_user_posts(resp):
    return resp.json()
```

## Заголовки

```python
app = FastHTTP(
    get_request={
        "headers": {"Authorization": "Bearer token"},
    },
)
```

## Обработка ошибок

```python
app = FastHTTP(debug=True)


@app.get(url="https://httpbin.org/status/404")
async def handle_404(resp):
    return f"Статус: {resp.status}"
```

Ошибки логируются автоматически.

## Параллельные запросы

```python
app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def get_post(resp):
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/users/1")
async def get_user(resp):
    return resp.json()


app.run()  # оба запроса выполняются параллельно
```

## Pydantic валидация

```python
from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    email: str


@app.get(url="https://jsonplaceholder.typicode.com/users/1", response_model=User)
async def get_user(resp):
    return resp.json()
```

## HTTP/2

```python
app = FastHTTP(http2=True)
```

Требует: `pip install fasthttp-client[http2]`

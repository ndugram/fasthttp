# Теги

Теги позволяют группировать и фильтровать запросы.

## Базовое использование

```python
from fasthttp import FastHTTP

app = FastHTTP()


@app.get(url="https://api.example.com/users", tags=["users"])
async def get_users(resp) -> dict:
    return resp.json()


@app.post(url="https://api.example.com/users", tags=["users"])
async def create_user(resp) -> dict:
    return resp.json()


@app.get(url="https://api.example.com/posts", tags=["posts"])
async def get_posts(resp) -> dict:
    return resp.json()


@app.post(url="https://api.example.com/posts", tags=["posts"])
async def create_post(resp) -> dict:
    return resp.json()
```

## Фильтрация по тегам

Запустите только запросы с определенными тегами:

```python
# Запустить только пользователей
app.run(tags=["users"])

# Запустить только посты
app.run(tags=["posts"])

# Запустить и пользователей и посты
app.run(tags=["users", "posts"])
```

## Несколько тегов

Запрос может иметь несколько тегов:

```python
@app.get(
    url="https://api.example.com/users",
    tags=["users", "v1", "api"]
)
async def get_users(resp) -> dict:
    return resp.json()
```

## Варианты использования

### Разработка vs Продакшен

```python
@app.get(url="https://dev.api.com/data", tags=["dev", "debug"])
async def dev_request(resp) -> dict:
    return resp.json()


@app.get(url="https://api.example.com/data", tags=["prod"])
async def prod_request(resp) -> dict:
    return resp.json()
```

### По ресурсу

```python
@app.get(url="https://api.example.com/users", tags=["users"])
async def get_users(resp) -> dict:
    return resp.json()


@app.get(url="https://api.example.com/orders", tags=["orders"])
async def get_orders(resp) -> dict:
    return resp.json()
```

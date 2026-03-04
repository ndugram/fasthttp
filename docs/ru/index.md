# FastHTTP

Современный async HTTP-клиент с красивым логированием.

## Установка

```bash
pip install fasthttp-client
```

## Быстрый пример

```python
from fasthttp import FastHTTP

app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/users/1")
async def main(resp):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

Вывод:

```
✔ GET https://jsonplaceholder.typicode.com/users/1 [200] 234.56ms
```

## Почему FastHTTP?

### Простой API

Без boilerplate, без сложной настройки:

```python
@app.get(url="https://api.example.com/data")
async def handler(resp):
    return resp.json()
```

### Красивое логирование

Видите что происходит — коды статуса, время, ошибки:

```
✔ GET https://api.example.com/users [200] 156.32ms
✔ POST https://api.example.com/users [201] 89.12ms
✗ GET https://api.example.com/missing [404]
```

Включите режим отладки для полных деталей:

```python
app = FastHTTP(debug=True)
```

### Все HTTP методы

```python
@app.get(url="https://api.example.com/users")
async def get_users(resp):
    return resp.json()


@app.post(url="https://api.example.com/users", json={"name": "John"})
async def create_user(resp):
    return resp.status


@app.put(url="https://api.example.com/users/1", json={"name": "Jane"})
async def update_user(resp):
    return resp.status


@app.patch(url="https://api.example.com/users/1", json={"age": 25})
async def patch_user(resp):
    return resp.status


@app.delete(url="https://api.example.com/users/1")
async def delete_user(resp):
    return resp.status
```

### Параметры запроса

```python
@app.get(url="https://api.example.com/search", params={"q": "fast", "page": 1})
async def search(resp):
    return resp.json()
```

### Параллельные запросы

Все зарегистрированные запросы выполняются параллельно:

```python
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


app.run()  # Все три запроса выполняются параллельно
```

## Возможности

| Возможность | Описание |
|-------------|----------|
| **Async** | Построен на httpx для высокой производительности |
| **Логирование** | Красивый цветной вывод с таймингом |
| **Типизация** | Полная поддержка IDE автодополнения |
| **Middleware** | Перехват и модификация запросов/ответов |
| **Pydantic** | Валидация ответов с моделями |
| **HTTP/2** | Опциональная поддержка HTTP/2 |

## Следующие шаги

- [Быстрый старт](quick-start.md) — начните за 2 минуты
- [CLI](cli.md) — командная строка
- [API](api-reference.md) — полная документация
- [Middleware](middleware.md) — перехват запросов
- [Конфигурация](configuration.md) — настройки

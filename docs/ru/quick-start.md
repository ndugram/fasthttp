# Быстрый старт

Начните работу менее чем за 2 минуты.

## Установка

```bash
pip install fasthttp-client
```

## Первый запрос

Создайте файл `example.py`:

```python
from fasthttp import FastHTTP

app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def main(resp):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

Запустите:

```bash
python example.py
```

Вывод:

```
✔ GET https://jsonplaceholder.typicode.com/posts/1 [200] 234.56ms
```

## HTTP методы

```python
app = FastHTTP()


@app.get(url="https://api.example.com/users")
async def get_users(resp):
    return resp.json()


@app.post(url="https://api.example.com/users", json={"name": "John"})
async def create_user(resp):
    return resp.status


@app.put(url="https://api.example.com/users/1", json={"name": "Jane"})
async def update_user(resp):
    return resp.json()


@app.patch(url="https://api.example.com/users/1", json={"age": 25})
async def patch_user(resp):
    return resp.status


@app.delete(url="https://api.example.com/users/1")
async def delete_user(resp):
    return resp.status
```

## Параметры запроса

```python
@app.get(url="https://api.example.com/search", params={"q": "fast", "page": 1})
async def search(resp):
    return resp.json()
```

## Заголовки

```python
app = FastHTTP(
    get_request={
        "headers": {
            "Authorization": "Bearer token",
            "User-Agent": "MyApp/1.0",
        },
    },
)
```

## Режим отладки

```python
app = FastHTTP(debug=True)
```

Показывает подробный вывод: заголовки, тело, тайминг.

## Обработка ошибок

Ошибки логируются автоматически:

```python
app = FastHTTP(debug=True)


@app.get(url="https://httpbin.org/status/404")
async def handle_error(resp):
    return f"Статус: {resp.status}"
```

## Несколько запросов

Все запросы выполняются параллельно:

```python
app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def get_post(resp):
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/users/1")
async def get_user(resp):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

## Возвращаемые значения

Обработчик может возвращать:

- `str` — строка
- `int` — код статуса
- `dict/list` — JSON
- `Response` — объект ответа

## Следующие шаги

- [Справочник API](api-reference.md) — полная документация
- [CLI](cli.md) — командная строка
- [Конфигурация](configuration.md) — настройки

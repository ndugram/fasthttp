# Параллельное выполнение

FastHTTP автоматически выполняет все зарегистрированные запросы параллельно.

## Как это работает

При вызове `app.run()`, FastHTTP:

1. Собирает все зарегистрированные маршруты
2. Создает асинхронную задачу для каждого маршрута
3. Выполняет все задачи параллельно с помощью `asyncio.gather()`
4. Ожидает завершения всех запросов
5. Логирует результаты

## Пример

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def get_post(resp: Response) -> dict:
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/users/1")
async def get_user(resp: Response) -> dict:
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/comments/1")
async def get_comment(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    # Все три запроса выполнятся параллельно
    app.run()
```

## Сравнение производительности

### Последовательное выполнение

```
Запрос 1: 150мс
Запрос 2: 120мс (после запроса 1)
Запрос 3: 110мс (после запроса 2)
Всего: ~380мс
```

### Параллельное выполнение (FastHTTP)

```
Запрос 1: 150мс
Запрос 2: 120мс
Запрос 3: 110мс
Всего: ~150мс (самый долгий запрос)
```

Вывод:

```
INFO    | fasthttp    | FastHTTP started
INFO    | fasthttp    | Sending 3 requests
INFO    | fasthttp    | GET https://jsonplaceholder.typicode.com/posts/1 200 150ms
INFO    | fasthttp    | GET https://jsonplaceholder.typicode.com/users/1 200 120ms
INFO    | fasthttp    | GET https://jsonplaceholder.typicode.com/comments/1 200 110ms
INFO    | fasthttp    | Done in 0.15s
```

## Когда это важно

Параллельное выполнение особенно полезно при:

- Множественных вызовах API
- Получении данных из нескольких сервисов
- Обработке нескольких ресурсов

Чем больше запросов, тем больше времени экономится.

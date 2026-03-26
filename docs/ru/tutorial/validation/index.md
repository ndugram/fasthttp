# Валидация

FastHTTP поддерживает валидацию запросов и ответов с помощью Pydantic.

## Обзор

- [Валидация Pydantic](pydantic-validation.md) - Валидация ответов API
- [Валидация запроса](request-validation.md) - Валидация данных перед отправкой
- [Валидация ошибок](error-validation.md) - Обработка ошибок API с Pydantic

## Быстрый пример

```python
from pydantic import BaseModel
from fasthttp import FastHTTP
from fasthttp.response import Response


class User(BaseModel):
    id: int
    name: str
    email: str


app = FastHTTP()


@app.get(
    url="https://jsonplaceholder.typicode.com/users/1",
    response_model=User
)
async def get_user(resp: Response) -> User:
    return resp.json()


app.run()
```

FastHTTP автоматически:
1. Получает JSON ответ
2. Валидирует через Pydantic
3. Возвращает валидный объект

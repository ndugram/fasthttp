# Валидация ошибок

Валидация ответов об ошибках API с использованием Pydantic моделей.

## Использование параметра responses

Параметр `responses` позволяет определять Pydantic модели для разных HTTP кодов статуса.

## Базовый пример

```python
from fasthttp import FastHTTP
from fasthttp.response import Response
from pydantic import BaseModel

app = FastHTTP(debug=True, security=False)


class Error404(BaseModel):
    message: str
    documentation_url: str
    status: str


@app.get(
    url="https://api.github.com/gist",
    responses={404: {"model": Error404}}
)
async def handle_404(resp: Response) -> dict:
    return resp.json()
```

Когда сервер возвращает ошибку:
1. FastHTTP ищет модель для этого статуса
2. Если найдена, валидирует JSON ответ
3. Валидированные данные доступны через resp.json()

## Несколько кодов статуса

```python
class Error404(BaseModel):
    message: str


class Error500(BaseModel):
    error: str
    details: str


@app.get(
    url="https://api.example.com/data",
    responses={
        404: {"model": Error404},
        500: {"model": Error500}
    }
)
async def handle_errors(resp: Response) -> dict:
    return resp.json()
```

## Успешные и ошибочные ответы

```python
class SuccessResponse(BaseModel):
    id: int
    name: str


class Error404(BaseModel):
    message: str


@app.get(
    url="https://api.example.com/users/1",
    response_model=SuccessResponse,
    responses={404: {"model": Error404}}
)
async def get_user(resp: Response) -> dict:
    return resp.json()
```

## Важные замечания

- `responses` работает только для API, возвращающих JSON с ошибками
- Если API возвращает ошибку без JSON, срабатывает стандартная обработка
- Модель должна соответствовать структуре ответа API
- Ключ в словаре - всегда целое число (HTTP код статуса)

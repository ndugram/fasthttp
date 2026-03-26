# Валидация Pydantic

Валидация ответов API с использованием Pydantic моделей.

## Базовая валидация ответа

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
```

## Вложенные модели

```python
class Address(BaseModel):
    street: str
    city: str
    zipcode: str


class User(BaseModel):
    id: int
    name: str
    email: str
    address: Address
```

## Списки объектов

```python
from typing import List

class Post(BaseModel):
    userId: int
    id: int
    title: str
    body: str


@app.get(
    url="https://jsonplaceholder.typicode.com/posts",
    response_model=List[Post]
)
async def get_posts(resp: Response) -> List[Post]:
    return resp.json()
```

## Опциональные поля

```python
from typing import Optional

class User(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
```

## Преобразование типов

Pydantic автоматически преобразует типы:

```python
class User(BaseModel):
    id: int  # Строка "1" станет int
    name: str
    is_active: bool  # "true" станет True
```

## Обработка ошибок

```python
from pydantic import BaseModel, ValidationError

@app.get(url="https://api.example.com/user", response_model=User)
async def get_user(resp: Response):
    try:
        return resp.json()
    except ValidationError as e:
        return {"error": "Invalid response format"}
```

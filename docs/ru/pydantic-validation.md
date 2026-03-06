# Pydantic Валидация

FastHTTP поддерживает валидацию ответов с помощью Pydantic.


## Базовая валидация

Определите Pydantic модель и укажите её в запросе:

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
async def get_user(resp: Response) -> User:
    return resp.json()
```

FastHTTP автоматически:
1. Получает JSON ответ
2. Валидирует через Pydantic
3. Возвращает валидный объект

## Вложенные модели

```python
from pydantic import BaseModel
from typing import List, Optional
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


class Address(BaseModel):
    street: str
    city: str
    zipcode: str


class User(BaseModel):
    id: int
    name: str
    email: str
    address: Address


@app.get(
    url="https://jsonplaceholder.typicode.com/users/1",
    response_model=User
)
async def get_user(resp: Response) -> User:
    return resp.json()
```

## Списки объектов

```python
from pydantic import BaseModel
from typing import List
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


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
from pydantic import BaseModel
from typing import Optional
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


class User(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None


@app.get(
    url="https://jsonplaceholder.typicode.com/users/1",
    response_model=User
)
async def get_user(resp: Response) -> User:
    return resp.json()
```

## Валидация с преобразованием

Pydantic автоматически преобразует типы:

```python
from pydantic import BaseModel
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


class User(BaseModel):
    id: int  # Строка "1" автоматически станет int
    name: str
    is_active: bool  # "true" -> True


@app.get(
    url="https://api.example.com/users/1",
    response_model=User
)
async def get_user(resp: Response) -> User:
    # Ответ: {"id": "1", "name": "John", "is_active": "true"}
    # Преобразуется в: User(id=1, name="John", is_active=True)
    return resp.json()
```

## Кастомные валидаторы

```python
from pydantic import BaseModel, validator
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


class User(BaseModel):
    name: str
    email: str
    
    @validator('email')
    def email_must_contain_at(cls, v):
        if '@' not in v:
            raise ValueError('Email must contain @')
        return v.lower()  # Автоматически в нижний регистр


@app.get(
    url="https://api.example.com/user",
    response_model=User
)
async def get_user(resp: Response) -> User:
    return resp.json()
```

## Обработка ошибок валидации

```python
from pydantic import BaseModel, ValidationError
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


class User(BaseModel):
    id: int
    name: str


@app.get(
    url="https://api.example.com/user",
    response_model=User
)
async def get_user(resp: Response):
    try:
        return resp.json()
    except ValidationError as e:
        print(f"Ошибка валидации: {e}")
        return {"error": "Invalid response format"}
```

## Типы данных Pydantic

FastHTTP поддерживает все типы Pydantic:

```python
from pydantic import BaseModel
from typing import List, Dict, Optional, Union
from datetime import datetime, date
from fasthttp import FastHTTP

app = FastHTTP()


class CompleteExample(BaseModel):
    # Примитивы
    name: str
    age: int
    is_active: bool
    balance: float
    
    # Коллекции
    tags: List[str]
    metadata: Dict[str, str]
    
    # Опциональные
    email: Optional[str] = None
    
    # Сложные типы
    created_at: datetime
    birth_date: date
    
    # Union
    status: Union[str, int]


@app.get(url="https://api.example.com/data", response_model=CompleteExample)
async def handler(resp):
    return resp.json()
```

## Смотрите также

- [Быстрый старт](quick-start.md) — основы
- [Конфигурация](configuration.md) — настройки
- [Pydantic Docs](https://pydantic-docs.helpmanual.io/) — документация Pydantic

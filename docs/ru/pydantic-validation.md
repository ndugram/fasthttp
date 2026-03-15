# Pydantic Валидация

FastHTTP поддерживает валидацию запросов и ответов с помощью Pydantic.


## Валидация запросов (request_model)

Валидация запросов позволяет проверить данные перед отправкой на сервер. Это полезно, чтобы не отправлять невалидные данные.

### Базовый пример

```python
from pydantic import BaseModel, Field
from fasthttp import FastHTTP

app = FastHTTP()

class UserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    age: int = Field(ge=0, le=150)

@app.post(
    url="https://api.example.com/users",
    json={"name": "John", "email": "john@example.com", "age": 25},
    request_model=UserRequest
)
async def create_user(resp):
    return resp.json()
```

Если данные не проходят валидацию, запрос не отправляется.

### Валидация с ошибкой

```python
@app.post(
    url="https://api.example.com/users",
    json={"name": "", "email": "invalid", "age": 200},
    request_model=UserRequest
)
async def create_user(resp):
    return resp.json()

# Запрос не пойдёт на сервер
# В логах: ERROR | Request validation failed: ...
```

### Валидация form data

```python
class LoginForm(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=8)

@app.post(
    url="https://api.example.com/login",
    data={"username": "john", "password": "secret123"},
    request_model=LoginForm
)
async def login(resp):
    return resp.json()
```

### Кастомные валидаторы

```python
from pydantic import BaseModel, field_validator

class UserRequest(BaseModel):
    name: str
    email: str
    
    @field_validator('email')
    @classmethod
    def email_must_contain_at(cls, v):
        if '@' not in v:
            raise ValueError('Email must contain @')
        return v.lower()

@app.post(
    url="https://api.example.com/users",
    json={"name": "John", "email": "JOHN@EXAMPLE.COM"},
    request_model=UserRequest
)
async def create_user(resp):
    return resp.json()
```

## Валидация ответов (response_model)

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

## Валидация ошибок API (responses)

Параметр `responses` позволяет определить Pydantic модели для обработки ошибок с разными HTTP статусами.

### Базовый пример

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
    responses={
        404: {"model": Error404}
    }
)
async def handle_404(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()
```

Когда сервер возвращает ошибку (4xx, 5xx):
1. FastHTTP ищет модель для этого статуса в `responses`
2. Если модель найдена, JSON ответ валидируется через Pydantic
3. Валидированный объект доступен через `resp.json()` или `resp._handler_result`
4. Handler вызывается с валидированными данными

### Несколько статусных кодов

```python
from fasthttp import FastHTTP
from fasthttp.response import Response
from pydantic import BaseModel

app = FastHTTP(debug=True, security=False)


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


if __name__ == "__main__":
    app.run()
```

### Работа с успешными и ошибочными ответами

```python
from fasthttp import FastHTTP
from fasthttp.response import Response
from pydantic import BaseModel

app = FastHTTP(debug=True, security=False)


class SuccessResponse(BaseModel):
    id: int
    name: str


class Error404(BaseModel):
    message: str


@app.get(
    url="https://api.example.com/users/1",
    response_model=SuccessResponse,
    responses={
        404: {"model": Error404}
    }
)
async def get_user(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()
```

### Использование с разными HTTP методами

```python
from fasthttp import FastHTTP
from fasthttp.response import Response
from pydantic import BaseModel

app = FastHTTP(debug=True, security=False)


class Error403(BaseModel):
    message: str


@app.post(
    url="https://api.example.com/users",
    json={"name": "John"},
    responses={
        403: {"model": Error403}
    }
)
async def create_user(resp: Response) -> dict:
    return resp.json()


@app.delete(
    url="https://api.example.com/users/1",
    responses={
        403: {"model": Error403},
        404: {"model": Error403}
    }
)
async def delete_user(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()
```

### Важные замечания

- `responses` работает только для API, которые возвращают JSON с ошибками
- Если API возвращает ошибку без JSON, валидация не пройдёт и будет вызвана стандартная обработка ошибок
- Модель должна соответствовать структуре JSON ответа API
- Ключ в словаре всегда целое число (HTTP статус код)

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

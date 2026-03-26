# Валидация запроса

Валидация данных запроса перед отправкой на сервер.

## Использование request_model

```python
from pydantic import BaseModel, Field


class UserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    age: int = Field(ge=0, le=150)


app = FastHTTP()


@app.post(
    url="https://api.example.com/users",
    json={"name": "John", "email": "john@example.com", "age": 25},
    request_model=UserRequest
)
async def create_user(resp):
    return resp.json()
```

Если данные не проходят валидацию, запрос не отправляется.

## Ошибка валидации

```python
# Этот запрос НЕ будет отправлен
@app.post(
    url="https://api.example.com/users",
    json={"name": "", "email": "invalid", "age": 200},
    request_model=UserRequest
)
async def create_user(resp):
    return resp.json()

# В логах: ERROR | Request validation failed: ...
```

## Валидация form data

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

## Зачем валидировать

Валидация запроса помогает:

- Обнаруживать ошибки перед отправкой
- Обеспечивать правильность формата данных
- Проверять ограничения (длина, паттерн, диапазон)

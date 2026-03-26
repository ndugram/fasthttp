# Аннотации типов Python

FastHTTP активно использует аннотации типов Python. Этот документ объясняет используемые типы.

## Зачем нужны аннотации

FastHTTP требует, чтобы все функции-обработчики имели явные аннотации типов:

1. **Аннотации параметров** - каждый параметр должен иметь тип
2. **Аннотация возвращаемого типа** - функция должна возвращать конкретный тип

Это основное требование фреймворка.

## Базовое использование

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.get(url="https://api.example.com/data")
async def get_data(resp: Response) -> dict:
    return resp.json()
```

## Типы возврата

FastHTTP поддерживает несколько типов возврата:

| Тип | Описание |
|-----|----------|
| `dict` | Автоматически преобразуется в JSON |
| `list` | Автоматически преобразуется в JSON |
| `str` | Возвращается как текст |
| `int` | Возвращается как число (часто код статуса) |
| `Response` | Возвращает весь объект ответа |
| `None` | Нет данных для возврата |

## Типичные ошибки

### Отсутствие аннотации параметра

```python
# Ошибка - отсутствует аннотация типа для resp
@app.get(url="https://api.example.com/data")
async def get_data(resp) -> dict:
    return resp.json()

# Исправление
async def get_data(resp: Response) -> dict:
    return resp.json()
```

### Отсутствие аннотации возвращаемого типа

```python
# Ошибка - отсутствует аннотация возвращаемого типа
@app.get(url="https://api.example.com/data")
async def get_data(resp: Response):
    return resp.json()

# Исправление
async def get_data(resp: Response) -> dict:
    return resp.json()
```

## Pydantic модели

При использовании Pydantic укажите модель как тип возврата:

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
    url="https://api.example.com/users/1",
    response_model=User
)
async def get_user(resp: Response) -> User:
    return resp.json()
```

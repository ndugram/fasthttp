# HTTP методы

FastHTTP поддерживает все основные HTTP методы.

## GET - получение данных

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.get(url="https://api.example.com/users")
async def get_users(resp: Response) -> dict:
    return resp.json()
```

## POST - создание данных

```python
@app.post(
    url="https://api.example.com/users",
    json={"name": "John", "email": "john@example.com"}
)
async def create_user(resp: Response) -> dict:
    return resp.json()
```

## PUT - полное обновление

```python
@app.put(
    url="https://api.example.com/users/1",
    json={"name": "Jane", "email": "jane@example.com"}
)
async def update_user(resp: Response) -> dict:
    return resp.json()
```

## PATCH - частичное обновление

```python
@app.patch(
    url="https://api.example.com/users/1",
    json={"age": 25}
)
async def patch_user(resp: Response) -> dict:
    return resp.json()
```

## DELETE - удаление данных

```python
@app.delete(url="https://api.example.com/users/1")
async def delete_user(resp: Response) -> int:
    return resp.status
```

## Возвращаемые значения

Обработчики могут возвращать разные типы:

```python
# Возврат dict - преобразуется в JSON
async def return_dict(resp: Response) -> dict:
    return {"message": "Hello"}

# Возврат списка
async def return_list(resp: Response) -> list:
    return [1, 2, 3]

# Возврат строки
async def return_string(resp: Response) -> str:
    return "Hello, World!"

# Возврат числа (код статуса)
async def return_number(resp: Response) -> int:
    return resp.status

# Возврат объекта Response
async def return_response(resp: Response) -> Response:
    return resp
```

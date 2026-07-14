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

## QUERY - сложные запросы на чтение с телом

`QUERY` — более новый HTTP-метод (предложен в IETF-черновике `draft-ietf-httpbis-safe-method-w-body`) для операций чтения, которые не помещаются в URL. Он безопасен и идемпотентен как `GET`, но несёт JSON-тело как `POST` — удобно для сложных запросов поиска/фильтрации.

```python
@app.query(
    url="https://api.example.com/users/search",
    json={"role": "admin", "active": True}
)
async def search_users(resp: Response) -> dict:
    return resp.json()
```

!!! note
    `QUERY` пока поддерживается не всеми серверами и прокси — используйте его только для API, которые явно документируют поддержку `QUERY`. Также этот метод не входит в стандартный набор методов OpenAPI Path Item Object, поэтому `QUERY`-маршруты не отображаются в Swagger UI (см. [OpenAPI](openapi/index.md)), хотя и попадают в сгенерированный `/openapi.json`.

## DELETE - удаление данных

```python
@app.delete(url="https://api.example.com/users/1")
async def delete_user(resp: Response) -> int:
    return resp.status
```

## HEAD - проверка endpoint'а

Возвращает только заголовки, без тела. Удобно для проверки существования ресурса или получения метаданных.

```python
@app.head(url="https://api.example.com/users")
async def check_users(resp: Response) -> int:
    return resp.status
```

## OPTIONS - разрешённые методы

Возвращает HTTP-методы, поддерживаемые endpoint'ом.

```python
@app.options(url="https://api.example.com/users")
async def allowed_methods(resp: Response) -> dict:
    return {"allow": resp.headers.get("allow", "")}
```

## Параметры декоратора

| Параметр | Описание |
|----------|----------|
| `url` | URL запроса (обязательный) |
| `params` | Query параметры |
| `json` | JSON тело (для POST, PUT, PATCH, QUERY) |
| `data` | Сырые байты |
| `files` | Загрузка файлов (multipart/form-data) |
| `tags` | Теги для группировки |
| `dependencies` | Список зависимостей |
| `response_model` | Модель Pydantic для валидации |
| `request_model` | Модель Pydantic для валидации запроса |
| `responses` | Модели Pydantic для ответов с ошибками |

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

# GraphQL

FastHTTP поддерживает GraphQL запросы и мутации через декоратор `@app.graphql()`.

## Введение

GraphQL — это язык запросов для API, который позволяет клиентам запрашивать только нужные данные. FastHTTP предоставляет удобный декоратор для работы с GraphQL эндпоинтами.

## Использование

### Query (чтение данных)

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.graphql(url="https://api.example.com/graphql")
async def get_user(resp: Response) -> dict:
    return {"query": "{ user(id: 1) { name email } }"}
```

### Mutation (запись данных)

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.graphql(url="https://api.example.com/graphql", operation_type="mutation")
async def create_user(resp: Response) -> dict:
    return {
        "query": "mutation { createUser(name: $name) { id name } }",
        "variables": {"name": "John"}
    }
```

## Параметры декоратора

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `url` | `str` | — | URL GraphQL эндпоинта (обязательно) |
| `operation_type` | `str` | `"query"` | Тип операции: `"query"` или `"mutation"` |
| `headers` | `dict` | `None` | Дополнительные заголовки |
| `timeout` | `float` | `30.0` | Таймаут запроса в секундах |
| `tags` | `list` | `None` | Теги для группировки запросов |

## Параметры возвращаемого словаря

Функция-обработчик должна возвращать словарь со следующими ключами:

| Ключ | Тип | Описание |
|------|-----|----------|
| `query` | `str` | GraphQL запрос (обязательно) |
| `variables` | `dict` | Переменные для запроса |
| `operation_name` | `str` | Имя операции (если их несколько) |

## Типы данных

### GraphQLResponse

Представляет ответ от GraphQL сервера:

```python
from fasthttp.graphql import GraphQLResponse

response = GraphQLResponse(
    data={"user": {"name": "John"}},
    errors=None,
    extensions={"traceId": "abc123"}
)

# Проверка на ошибки
if response.ok:
    print(response.data)
elif response.has_errors:
    print(response.errors)
```

**Свойства GraphQLResponse:**

| Свойство | Тип | Описание |
|----------|-----|----------|
| `data` | `dict \| None` | Данные ответа |
| `errors` | `list \| None` | Список ошибок |
| `extensions` | `dict \| None` | Дополнительные данные |
| `ok` | `bool` | `True` если нет ошибок |
| `has_errors` | `bool` | `True` если есть ошибки |

## Примеры

### Создание пользователя

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.graphql(url="https://api.example.com/graphql", operation_type="mutation")
async def create_user(resp: Response) -> dict:
    return {
        "query": """
            mutation CreateUser($name: String!, $email: String!) {
                createUser(name: $name, email: $email) {
                    id
                    name
                    email
                }
            }
        """,
        "variables": {
            "name": "John Doe",
            "email": "john@example.com"
        }
    }


if __name__ == "__main__":
    app.run()
```

### Получение списка с фильтрацией

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.graphql(url="https://api.example.com/graphql")
async def get_users(resp: Response) -> dict:
    return {
        "query": """
            query GetUsers($limit: Int!, $offset: Int!) {
                users(limit: $limit, offset: $offset) {
                    id
                    name
                    email
                }
            }
        """,
        "variables": {
            "limit": 10,
            "offset": 0
        }
    }
```

### С авторизацией

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.graphql(
    url="https://api.example.com/graphql",
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
async def get_profile(resp: Response) -> dict:
    return {"query": "{ me { name email } }"}
```

### Использование с другими методами

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.get(url="https://httpbin.org/get")
async def http_get(resp: Response) -> dict:
    return resp.json()


@app.graphql(url="https://api.example.com/graphql")
async def graphql_query(resp: Response) -> dict:
    return {"query": "{ version }"}


# Запустит оба запроса
app.run()

# Запустит только GraphQL
app.run(tags=["graphql"])
```

## Смотрите также

- [Middleware](middleware.md) — для добавления логики
- [Конфигурация](configuration.md) — настройки
- [Быстрый старт](quick-start.md) — основы

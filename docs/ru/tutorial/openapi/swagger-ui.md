# Swagger UI

Интерактивная документация и тестирование API.

## Быстрый старт

Запустите приложение с `web_run()`:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.get("https://httpbin.org/get")
async def get_data(resp: Response) -> dict:
    return resp.json()


app.web_run()
```

После запуска откройте в браузере:

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **OpenAPI схема**: `http://127.0.0.1:8000/openapi.json`

## Доступные endpoints

| Endpoint        | Описание                       |
| --------------- | ------------------------------ |
| `/docs`         | Интерфейс Swagger UI           |
| `/openapi.json` | OpenAPI схема в JSON           |
| `/request`      | Прокси для выполнения запросов |

## Использование Swagger UI

1. Найдите нужный endpoint в списке
2. Нажмите для раскрытия
3. Нажмите кнопку **"Execute"**
4. Просмотрите ответ в разделе **Response**

## Кастомный хост и порт

```python
app.web_run(host="0.0.0.0", port=8080)
```

## Кастомный base URL для документации

```python
app.web_run(base_url="/api")
```

Теперь документация будет доступна по адресу `http://127.0.0.1:8000/api/docs`.

## Пример

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str


app = FastHTTP()


@app.get("https://jsonplaceholder.typicode.com/users/1", response_model=User)
async def get_user(resp: Response) -> dict:
    return resp.json()


app.web_run()
```

Откройте `http://127.0.0.1:8000/docs` для тестирования запросов.

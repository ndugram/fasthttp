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
- **ReDoc**: `http://127.0.0.1:8000/redoc`
- **OpenAPI схема**: `http://127.0.0.1:8000/openapi.json`

## Доступные endpoints

| Endpoint        | Описание                                      |
| --------------- | ---------------------------------------------- |
| `/docs`         | Интерфейс Swagger UI (тёмная тема — переключатель справа сверху) |
| `/redoc`        | ReDoc — альтернативный read-only просмотр      |
| `/openapi.json` | OpenAPI схема в JSON                           |
| `/request`      | Прокси для выполнения запросов                 |

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

## Кастомизация информации об API

Параметры `title`, `version` и `description` в `FastHTTP` управляют заголовком в Swagger UI:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(
    title="Payments API",
    version="3.1.0",
    description="""
## Payments API

Списание средств, возвраты и история транзакций.

Поддерживает **Markdown**.
""",
)


@app.get("https://api.example.com/transactions")
async def list_transactions(resp: Response) -> list:
    """Список последних транзакций."""
    return resp.json()


app.web_run()
```

| Параметр | По умолчанию | Описание |
|----------|--------------|----------|
| `title` | `"FastHTTP API"` | Название API в заголовке Swagger UI |
| `version` | `"1.0.0"` | Строка версии рядом с названием |
| `description` | `""` | Markdown-описание под заголовком |

## Security Schemes в Swagger UI

Если маршруты используют `auth=`, FastHTTP автоматически добавляет схему безопасности в `components/securitySchemes` и показывает значок замка на защищённых операциях.

```python
from fasthttp import FastHTTP, BearerAuth, BasicAuth
from fasthttp.response import Response

app = FastHTTP(title="Secure API", version="1.0.0")


@app.get(
    "https://api.example.com/profile",
    auth=BearerAuth(token="my-token"),
    tags=["users"],
)
async def get_profile(resp: Response) -> dict:
    """Защищён Bearer-токеном."""
    return resp.json()


@app.get(
    "https://legacy.example.com/data",
    auth=BasicAuth(username="admin", password="pass"),
    tags=["legacy"],
)
async def get_legacy_data(resp: Response) -> dict:
    """Защищён Basic-аутентификацией."""
    return resp.json()


@app.get("https://api.example.com/status", tags=["public"])
async def status(resp: Response) -> dict:
    """Публичный — без замка."""
    return resp.json()


app.web_run()
```

FastHTTP добавляет схемы автоматически:

| Класс | Имя схемы | OpenAPI тип |
|-------|-----------|-------------|
| `BearerAuth` | `bearerAuth` | `http / bearer / JWT` |
| `BasicAuth` | `basicAuth` | `http / basic` |
| `DigestAuth` | `digestAuth` | `http / digest` |
| `OAuth2ClientCredentials` | `oauth2ClientCredentials` | `oauth2 / clientCredentials` |

Схема добавляется в документ только если хотя бы один маршрут использует соответствующий `auth=`.

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

# Аутентификация

FastHTTP предоставляет встроенные классы аутентификации, которые применяются на уровне отдельного маршрута через параметр `auth` в любом декораторе.

## Доступные классы

| Класс | Назначение |
|-------|------------|
| `BasicAuth(username, password)` | HTTP Basic — base64-кодированные учётные данные |
| `DigestAuth(username, password)` | HTTP Digest — challenge-response рукопожатие |
| `BearerAuth(token)` | Bearer-токен — OAuth2, JWT, API-ключи |

Все три импортируются напрямую из `fasthttp` и конвертируются в эквиваленты httpx в момент запроса.

## BasicAuth

Отправляет заголовок `Authorization: Basic <base64>` с каждым запросом на маршрут:

```python
from fasthttp import FastHTTP, BasicAuth
from fasthttp.response import Response

app = FastHTTP()


@app.get("https://api.example.com/profile", auth=BasicAuth("alice", "s3cr3t"))
async def get_profile(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()
```

## DigestAuth

Выполняет полное HTTP Digest challenge-response рукопожатие автоматически:

```python
from fasthttp import FastHTTP, DigestAuth
from fasthttp.response import Response

app = FastHTTP()


@app.get("https://api.example.com/data", auth=DigestAuth("alice", "s3cr3t"))
async def get_data(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()
```

## BearerAuth

Отправляет заголовок `Authorization: Bearer <token>` — используется для OAuth2 access токенов, JWT и статических API-ключей:

```python
from fasthttp import FastHTTP, BearerAuth
from fasthttp.response import Response

app = FastHTTP()


@app.get("https://api.example.com/users", auth=BearerAuth("my-jwt-token"))
async def get_users(resp: Response) -> list:
    return resp.json()


if __name__ == "__main__":
    app.run()
```

## OAuth2ClientCredentials

Получает токен через грант **Client Credentials** и автоматически обновляет его до истечения срока действия:

```python
from fasthttp import FastHTTP
from fasthttp.auth import OAuth2ClientCredentials
from fasthttp.response import Response

app = FastHTTP()

auth = OAuth2ClientCredentials(
    token_url="https://auth.example.com/oauth/token",
    client_id="my-client",
    client_secret="my-secret",
    scopes=["read", "write"],
)


@app.get("https://api.example.com/users", auth=auth)
async def get_users(resp: Response) -> list:
    return resp.json()


if __name__ == "__main__":
    app.run()
```

Токен запрашивается лениво (при первом запросе) и кешируется. FastHTTP автоматически запрашивает новый токен за 60 секунд до истечения текущего, основываясь на поле `expires_in` в ответе токен-эндпоинта.

| Параметр | Обязательный | Описание |
|----------|-------------|----------|
| `token_url` | Да | URL токен-эндпоинта OAuth2 |
| `client_id` | Да | Идентификатор клиента |
| `client_secret` | Да | Секрет клиента |
| `scopes` | Нет | Список строк запрашиваемых разрешений |
| `extra` | Нет | Дополнительные поля, отправляемые в теле запроса токена |

## Auth в роутерах

Параметр `auth` работает на всех декораторах `Router`:

```python
from fasthttp import FastHTTP, Router, BearerAuth
from fasthttp.response import Response

TOKEN = "my-service-token"

app = FastHTTP()
payments = Router(base_url="https://payments.example.com", prefix="/v1")


@payments.post("/charge", auth=BearerAuth(TOKEN))
async def charge(resp: Response) -> dict:
    return resp.json()


@payments.get("/history", auth=BearerAuth(TOKEN))
async def history(resp: Response) -> list:
    return resp.json()


app.include_router(payments)

if __name__ == "__main__":
    app.run()
```

## Разные типы auth на разных маршрутах

Разные маршруты могут использовать разные классы аутентификации:

```python
from fasthttp import FastHTTP, BasicAuth, BearerAuth
from fasthttp.response import Response

app = FastHTTP()


@app.get("https://legacy.example.com/api", auth=BasicAuth("admin", "pass"))
async def legacy(resp: Response) -> dict:
    return resp.json()


@app.get("https://modern.example.com/api", auth=BearerAuth("jwt-token"))
async def modern(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()
```

## Без аутентификации

Без `auth` (по умолчанию `None`) заголовки аутентификации не отправляются:

```python
@app.get("https://api.example.com/public")
async def public(resp: Response) -> dict:
    return resp.json()
```

## Совместно с raise_for_status

`auth` и `raise_for_status` можно использовать вместе на одном маршруте:

```python
from fasthttp import FastHTTP, BearerAuth
from fasthttp.exceptions import FastHTTPBadStatusError
from fasthttp.response import Response

app = FastHTTP()


@app.get(
    "https://api.example.com/secure",
    auth=BearerAuth("my-token"),
    raise_for_status=True,
)
async def secure(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    try:
        app.run()
    except FastHTTPBadStatusError as e:
        print(f"HTTP {e.status_code} на {e.url}")
```

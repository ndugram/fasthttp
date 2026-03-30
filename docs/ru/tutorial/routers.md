# Роутеры

`Router` помогает разбивать большие приложения FastHTTP на небольшие
переиспользуемые группы маршрутов.

Это полезно, когда нужно:

- держать связанные запросы вместе
- переиспользовать группы маршрутов в нескольких приложениях
- задавать общий `prefix`, `base_url`, `tags` или `dependencies`
- строить вложенные деревья роутеров

## Базовое использование

```python
from fasthttp import FastHTTP, Router
from fasthttp.response import Response

app = FastHTTP()
users = Router(base_url="https://api.example.com", prefix="/users", tags=["users"])


@users.get("/me")
async def get_me(resp: Response) -> dict:
    return resp.json()


@users.get("/list")
async def get_users(resp: Response) -> dict:
    return resp.json()


app.include_router(users)
```

В результате будут сформированы URL:

- `https://api.example.com/users/me`
- `https://api.example.com/users/list`

## Параметры Router

Роутер можно настроить через:

- `base_url` для хоста, например `https://api.example.com`
- `prefix` для общего пути, например `/v1`
- `tags`, которые наследуются всеми маршрутами роутера
- `dependencies`, которые наследуются всеми маршрутами роутера

```python
router = Router(
    base_url="https://api.example.com",
    prefix="/v1",
    tags=["api", "v1"],
)
```

## include_router()

Подключение роутера к приложению:

```python
app.include_router(router)
```

Также значения можно переопределить при подключении:

```python
app.include_router(
    router,
    prefix="/public",
    tags=["public"],
    base_url="https://gateway.example.com",
)
```

Значения, переданные в `include_router()`, применяются перед собственными
значениями роутера.

## Вложенные роутеры

Роутеры могут включать другие роутеры.

```python
from fasthttp import FastHTTP, Router
from fasthttp.response import Response

app = FastHTTP()

api = Router(base_url="https://api.example.com", prefix="/v1", tags=["api"])
users = Router(prefix="/users", tags=["users"])


@users.get("/me")
async def get_me(resp: Response) -> dict:
    return resp.json()


api.include_router(users)
app.include_router(api)
```

Итоговый URL:

- `https://api.example.com/v1/users/me`

Итоговые теги:

- `["api", "users"]`

## Роутеры в нескольких файлах

На практике роутеры обычно выносят в отдельные модули, а затем собирают в одном
месте через `include_router()`.

Пример структуры:

```text
src/
  clients/
    integrations/
      __init__.py
      users.py
      orders.py
      payments.py
```

### `users.py`

```python
from fasthttp import Router
from fasthttp.response import Response

router = Router(prefix="/users", tags=["users"])


@router.get("/me")
async def get_me(resp: Response) -> dict:
    return resp.json()


@router.get("/list")
async def get_users(resp: Response) -> dict:
    return resp.json()
```

### `orders.py`

```python
from fasthttp import Router
from fasthttp.response import Response

router = Router(prefix="/orders", tags=["orders"])


@router.get("/")
async def get_orders(resp: Response) -> dict:
    return resp.json()
```

### `__init__.py`

В стиле FastAPI или aiogram можно сделать общий setup-файл, который собирает все
роутеры в одном месте:

```python
from fasthttp import Router

from src.clients.integrations import orders, payments, users


def setup_integrations_router() -> Router:
    router = Router()

    router.include_router(users.router)
    router.include_router(orders.router)
    router.include_router(payments.router)

    return router
```

### Подключение в приложении

```python
from fasthttp import FastHTTP

from src.clients.integrations import setup_integrations_router

app = FastHTTP(base_url="https://api.example.com")
app.include_router(setup_integrations_router())
```

Это особенно удобно, когда проект становится большим и роутеры нужно собирать
так же, как в FastAPI:

```python
router.include_router(users.router)
router.include_router(orders.router)
router.include_router(payments.router)
```

Или в более минималистичном стиле, как в aiogram:

```python
from fasthttp import Router

from src.handlers import auth, users


def setup_handlers_router() -> Router:
    router = Router()

    router.include_router(auth.router)
    router.include_router(users.router)

    return router
```

## Относительные URL и base_url

Если маршрут использует относительный путь, например `"/me"`, FastHTTP должен
получить `base_url` где-то в дереве роутеров.

```python
router = Router()


@router.get("/me")
async def get_me(resp: Response) -> dict:
    return resp.json()


app.include_router(router, base_url="https://api.example.com")
```

Если `base_url` не передан, FastHTTP выбросит `ValueError`.

## Когда использовать роутеры

Используйте роутеры, когда в проекте есть:

- несколько ресурсов API, например users, orders, payments
- разные версии API, например `/v1` и `/v2`
- группы маршрутов с общими тегами или зависимостями
- необходимость поддерживать большую коллекцию запросов в порядке

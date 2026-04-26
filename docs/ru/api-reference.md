# Справочник API

Полная документация по всем классам и функциям FastHTTP.

## Класс FastHTTP

Основной класс приложения.

```python
from fasthttp import FastHTTP
```

### Конструктор

```python
app = FastHTTP(
    debug: bool = False,
    http2: bool = False,
    get_request: dict = {},
    post_request: dict = {},
    put_request: dict = {},
    patch_request: dict = {},
    delete_request: dict = {},
    head_request: dict = {},
    options_request: dict = {},
    middleware: list = [],
    security: bool = True,
    lifespan: Callable = None,
)
```

### Параметры

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `debug` | `bool` | `False` | Режим отладки |
| `http2` | `bool` | `False` | Использовать HTTP/2 |
| `get_request` | `dict` | `{}` | Настройки для GET |
| `post_request` | `dict` | `{}` | Настройки для POST |
| `put_request` | `dict` | `{}` | Настройки для PUT |
| `patch_request` | `dict` | `{}` | Настройки для PATCH |
| `delete_request` | `dict` | `{}` | Настройки для DELETE |
| `head_request` | `dict` | `{}` | Настройки для HEAD |
| `options_request` | `dict` | `{}` | Настройки для OPTIONS |
| `middleware` | `list` | `[]` | Список middleware |
| `security` | `bool` | `True` | Включить встроенную защиту |
| `lifespan` | `Callable` | `None` | Контекстный менеджер для startup/shutdown |

### Методы

#### run()

Запускает выполнение запросов.

```python
app.run(
    tags: list = None,
)
```

**Параметры:**
- `tags` — список тегов для фильтрации запросов

**Пример:**

```python
app.run()  # Запустить все
app.run(tags=["users"])  # Только с тегом users
```

### Lifespan

Контекстный менеджер для выполнения кода до и после запросов.

```python
from contextlib import asynccontextmanager
from fasthttp import FastHTTP

@asynccontextmanager
async def lifespan(app: FastHTTP):
    # Startup
    app.token = await load_token()
    yield
    # Shutdown
    await cleanup()

app = FastHTTP(lifespan=lifespan)
```

**Параметры:**
- `app` — экземпляр FastHTTP, можно добавлять атрибуты

**Примеры использования:**

```python
# Загрузка конфигурации
@asynccontextmanager
async def lifespan(app):
    app.config = load_config()
    yield

# Подключение к Redis
@asynccontextmanager
async def lifespan(app):
    app.redis = await aioredis.from_url("redis://localhost")
    yield
    await app.redis.close()

# Сбор статистики
@asynccontextmanager
async def lifespan(app):
    app.stats = {"requests": 0}
    yield
    print(f"Total: {app.stats['requests']} requests")
```

## Декораторы HTTP методов

### @app.get()

```python
@app.get(
    url: str,
    params: dict = None,
    tags: list = [],
    dependencies: list = [],
    response_model: type = None,
    request_model: type = None,
    responses: dict = None,
    get_request: dict = None,
)
```

### @app.post()

```python
@app.post(
    url: str,
    json: dict = None,
    data: bytes = None,
    params: dict = None,
    tags: list = [],
    dependencies: list = [],
    response_model: type = None,
    request_model: type = None,
    responses: dict = None,
    post_request: dict = None,
)
```

### @app.put()

```python
@app.put(
    url: str,
    json: dict = None,
    data: bytes = None,
    params: dict = None,
    tags: list = [],
    dependencies: list = [],
    response_model: type = None,
    request_model: type = None,
    responses: dict = None,
    put_request: dict = None,
)
```

### @app.patch()

```python
@app.patch(
    url: str,
    json: dict = None,
    data: bytes = None,
    params: dict = None,
    tags: list = [],
    dependencies: list = [],
    response_model: type = None,
    request_model: type = None,
    responses: dict = None,
    patch_request: dict = None,
)
```

### @app.delete()

```python
@app.delete(
    url: str,
    params: dict = None,
    tags: list = [],
    dependencies: list = [],
    response_model: type = None,
    request_model: type = None,
    responses: dict = None,
)
```

### @app.head()

```python
@app.head(
    url: str,
    params: dict = None,
    tags: list = [],
    dependencies: list = [],
    response_model: type = None,
    request_model: type = None,
    responses: dict = None,
)
```

### @app.options()

```python
@app.options(
    url: str,
    params: dict = None,
    tags: list = [],
    dependencies: list = [],
    response_model: type = None,
    request_model: type = None,
    responses: dict = None,
)
```

### Параметры декораторов

| Параметр | Тип | Описание |
|----------|-----|----------|
| `url` | `str` | URL запроса |
| `params` | `dict` | Query параметры |
| `json` | `dict` | JSON тело запроса |
| `data` | `bytes` | Raw данные запроса |
| `tags` | `list` | Теги для группировки |
| `dependencies` | `list` | Зависимости |
| `response_model` | `type[BaseModel]` | Pydantic модель для валидации ответа |
| `request_model` | `type[BaseModel]` | Pydantic модель для валидации запроса |
| `responses` | `dict[int, dict[Literal["model"], type[BaseModel]]]` | Pydantic модели для валидации ошибок API |

### Требования к аннотациям

FastHTTP требует, чтобы все функции-обработчики имели явные аннотации типов:

1. **Аннотация параметров** — каждый параметр должен иметь тип
2. **Аннотация возвращаемого типа** — функция должна возвращать конкретный тип

**Пример корректной функции:**

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()

@app.get(url="https://api.example.com/data")
async def get_data(resp: Response) -> dict:  # ✅ Аннотации есть
    return resp.json()
```

**Примеры ошибок:**

```python
# ❌ Отсутствует аннотация параметра
@app.get(url="https://api.example.com/data")
async def get_data(resp) -> dict:
    return resp.json()

# ❌ Отсутствует аннотация возвращаемого типа
@app.get(url="https://api.example.com/data")
async def get_data(resp: Response):
    return resp.json()

# ❌ Отсутствуют обе аннотации
@app.get(url="https://api.example.com/data")
async def get_data(resp):
    return resp.json()
```

**Ошибки при отсутствии аннотаций:**

```
TypeError: Parameter 'resp' in function 'get_data' must have a type annotation
TypeError: Function 'get_data' must explicitly define return type annotation
```

## Зависимости

### Depends()

```python
from fasthttp import Depends
```

Создаёт зависимость для модификации запроса.

```python
Depends(
    func: Callable,
    use_cache: bool = True,
    scope: str = "function",
)
```

**Параметры:**
- `func` — async функция с сигнатурой `(route, config) -> config`
- `use_cache` — кэшировать результат
- `scope` — область видимости ("function" или "request")

**Пример:**

```python
async def add_auth(route, config):
    config.setdefault("headers", {})["Authorization"] = "Bearer token"
    return config

@app.get(url="/data", dependencies=[Depends(add_auth)])
async def handler(resp):
    return resp.json()
```

## Middleware

### BaseMiddleware

Базовый класс для создания middleware.

```python
from fasthttp.middleware import BaseMiddleware

class MyMiddleware(BaseMiddleware):
    async def before_request(self, route, config):
        return config
    
    async def after_response(self, response, route, config):
        return response
    
    async def on_error(self, error, route, config):
        raise error
```

### CacheMiddleware

Встроенный middleware для кеширования.

```python
from fasthttp import CacheMiddleware

app = FastHTTP(
    middleware=[CacheMiddleware(ttl=3600, max_size=100)]
)
```

**Параметры:**
- `ttl` — время жизни кэша в секундах
- `max_size` — максимальное количество закэшированных запросов

## Response

Объект ответа.

```python
@app.get(url="https://api.example.com/data")
async def handler(resp: Response):
    # Доступные атрибуты
    status = resp.status       # Код статуса (int)
    text = resp.text           # Текст ответа (str)
    json_data = resp.json()    # JSON данные (dict/list)
    headers = resp.headers     # Заголовки ответа (dict)
    content = resp.content     # Сырые байты (bytes)
```

## CLI

### fasthttp

```bash
fasthttp <method> <url> [options]
```

**Методы:** `get`, `post`, `put`, `patch`, `delete`

**Опции:**

| Опция | Описание |
|-------|----------|
| `-H, --header` | Заголовок |
| `-p, --param` | Query параметр |
| `--json` | JSON тело |
| `--timeout` | Таймаут |
| `--debug` | Режим отладки |
| `-o, --output` | Сохранить в файл |
| `--format` | Формат вывода |

## Типы данных

### Route

Объект с информацией о маршруте:

```python
route.method          # HTTP метод
route.url             # URL
route.params          # Query параметры
route.json            # JSON тело
route.data            # Raw данные
route.tags            # Теги
route.dependencies    # Зависимости
```

### Config

Словарь с конфигурацией запроса:

```python
config.get("headers", {})       # Заголовки
config.get("timeout", 30.0)     # Таймаут
config.get("allow_redirects", True)  # Редиректы
```

## Безопасность

В FastHTTP встроена система безопасности, которая работает автоматически.

### Параметр security

```python
app = FastHTTP(security=True)   # Защита включена (по умолчанию)
app = FastHTTP(security=False)  # Защита отключена
```

### Что включено

- **SSRF защита** — блокировка запросов к localhost и приватным IP
- **Маскирование secrets** — скрытие Authorization, Cookie в логах
- **Circuit Breaker** — автоматическая блокировка падающих хостов
- **Лимиты** — timeout, max response size, max concurrent requests
- **Защита заголовков** — очистка от CRLF символов
- **Защита редиректов** — блокировка file://, javascript:, internal IPs

### Пример

```python
from fasthttp import FastHTTP

app = FastHTTP()  # security=True по умолчанию

@app.get(url="https://api.example.com/data")
async def handler(resp):
    return resp.json()

app.run()  # Защита работает автоматически
```

Подробнее в [Безопасность](security.md).

## GraphQL

### @app.graphql()

Декоратор для выполнения GraphQL запросов и мутаций.

```python
@app.graphql(
    url: str,
    operation_type: str = "query",
    headers: dict = None,
    timeout: float = 30.0,
    tags: list = [],
)
```

**Параметры:**

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `url` | `str` | — | GraphQL эндпоинт (обязательно) |
| `operation_type` | `str` | `"query"` | `"query"` или `"mutation"` |
| `headers` | `dict` | `None` | Дополнительные заголовки |
| `timeout` | `float` | `30.0` | Таймаут в секундах |
| `tags` | `list` | `None` | Теги для группировки |

**Пример Query:**

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.graphql(url="https://api.example.com/graphql")
async def get_user(resp: Response) -> dict:
    return {"query": "{ user(id: 1) { name email } }"}
```

**Пример Mutation:**

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.graphql(url="https://api.example.com/graphql", operation_type="mutation")
async def create_user(resp: Response) -> dict:
    return {
        "query": "mutation { createUser(name: $name) { id } }",
        "variables": {"name": "John"}
    }
```

### GraphQLResponse

Представляет ответ от GraphQL сервера.

```python
from fasthttp.graphql import GraphQLResponse

response = GraphQLResponse(
    data: dict = None,
    errors: list = None,
    extensions: dict = None,
)
```

**Свойства:**

| Свойство | Тип | Описание |
|----------|-----|----------|
| `data` | `dict \| None` | Данные ответа |
| `errors` | `list \| None` | Список ошибок |
| `extensions` | `dict \| None` | Дополнительные данные |
| `ok` | `bool` | `True` если нет ошибок |
| `has_errors` | `bool` | `True` если есть ошибки |

## Смотрите также

- [Быстрый старт](quick-start.md) — основы
- [Конфигурация](configuration.md) — настройки
- [Зависимости](dependencies.md) — модификация запросов
- [Middleware](middleware.md) — глобальная логика
- [GraphQL](graphql.md) — подробная документация

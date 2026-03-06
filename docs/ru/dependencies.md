# Зависимости (Dependencies)

Зависимости — это мощный и интуитивно понятный способ модификации запросов перед их отправкой. В отличие от middleware, зависимости применяются к конкретным запросам, а не глобально ко всему приложению.

## Что такое Dependency Injection?

В программировании "Dependency Injection" означает, что ваш код (в нашем случае — обработчики запросов) может объявлять, что ему нужно для работы, а система сама позаботится о предоставлении этих зависимостей.

Это очень полезно для:

- Общей логики (повторяющийся код)
- Общих подключений к базам данных
- Безопасности и аутентификации
- Логирования и трейсинга
- И многого другого...

При этом вы избегаете дублирования кода.

## Быстрый пример

Давайте начнём с простого примера:

```python
from fasthttp import FastHTTP, Depends
from fasthttp.response import Response

app = FastHTTP()


async def add_auth_header(route, config):
    """Добавляет заголовок авторизации."""
    config.setdefault("headers", {})["Authorization"] = "Bearer my-token"
    return config


@app.get(
    url="https://api.example.com/users",
    dependencies=[Depends(add_auth_header)]
)
async def get_users(resp: Response):
    return resp.json()
```

При запуске `add_auth_header` выполнится перед запросом и добавит токен в заголовки.

## Почему Dependencies, а не Middleware?

| Особенность | Middleware | Dependencies |
|-------------|------------|--------------|
| Глобальное применение | ✅ Да | ❌ Нет |
| Применение к конкретному запросу | ❌ Нет | ✅ Да |
| Сложность реализации | Выше | Ниже |
| Может модифицировать response | ✅ Да | ❌ Нет |
| Может вернуть произвольное значение | ❌ Нет | ✅ Да |

### Когда использовать Middleware

- Нужно применить логику абсолютно ко всем запросам
- Требуется модификация ответа после запроса
- Нужна централизованная обработка ошибок

### Когда использовать Dependencies

- Логика нужна только для определённых запросов
- Простая модификация конфигурации запроса
- Более декларативный и понятный код

## Создание зависимости

Зависимость — это функция с двумя параметрами (`route` и `config`). Поддерживаются как async, так и синхронные функции:

```python
# Async функция
async def my_dependency_async(route, config):
    config.setdefault("headers", {})["X-Custom"] = "value"
    return config

# Синхронная функция
def my_dependency_sync(route, config):
    config.setdefault("headers", {})["X-Custom"] = "value"
    return config
```

Обе функции работают одинаково — система автоматически определяет тип функции.

### Доступные параметры route

Объект `route` содержит всю информацию о запросе:

```python
route.method      # HTTP метод: "GET", "POST", "PUT", "PATCH", "DELETE"
route.url         # Полный URL запроса
route.params      # Query параметры (словарь)
route.json        # JSON тело запроса (словарь)
route.data        # Raw данные
route.tags        # Теги запроса (список)
route.dependencies  # Список зависимостей маршрута
route.handler     # Обработчик ответа
route.response_model  # Pydantic модель для валидации
```

### Доступные параметры config

Объект `config` содержит настройки запроса:

```python
config.get("headers", {})      # Заголовки запроса
config.get("timeout", 30.0)    # Таймаут в секундах
config.get("allow_redirects", True)  # Разрешить редиректы
```

## Параметры функции Depends

Функция `Depends()` принимает дополнительные параметры:

```python
Depends(
    func,              # Ваша async функция-зависимость
    use_cache=True,    # Кэшировать результат
    scope="function"   # Область видимости: "function" или "request"
)
```

### Параметр use_cache

Если `use_cache=True` (по умолчанию), результат зависимости кэшируется на время выполнения запроса. Это полезно для дорогих вычислений, которые не нужно выполнять несколько раз:

```python
async def get_token(route, config):
    # Дорогая операция — например, запрос к другому API
    token = await fetch_token_from_auth_server()
    config["headers"]["Authorization"] = f"Bearer {token}"
    return config


# Токен получится один раз и будет использован для всех запросов
@app.get(url="/api/data", dependencies=[Depends(get_token, use_cache=True)])
async def handler1(resp): ...


@app.get(url="/api/other", dependencies=[Depends(get_token, use_cache=True)])
async def handler2(resp): ...
```

### Параметр scope

Параметр `scope` определяет, когда выполняется зависимость:

- `"function"` (по умолчанию) — выполняется перед обработчиком запроса
- `"request"` — выполняется вокруг всего цикла запроса-ответа

```python
async def log_request(route, config):
    print(f"Начало запроса: {route.method} {route.url}")
    return config


# scope="function" — выполнится только перед запросом
@app.get(url="/data", dependencies=[Depends(log_request, scope="function")])
async def handler(resp): ...
```

## Практические примеры

### Пример 1: Добавление токена авторизации

Самый частый случай использования — добавление токена:

```python
async def add_bearer_token(route, config):
    """Добавляет Bearer токен в заголовки запроса."""
    token = "ваш-секретный-токен"
    config.setdefault("headers", {})["Authorization"] = f"Bearer {token}"
    return config


@app.get(
    url="https://api.example.com/users",
    dependencies=[Depends(add_bearer_token)]
)
async def get_users(resp: Response):
    """Получить список пользователей."""
    return resp.json()


@app.post(
    url="https://api.example.com/users",
    json={"name": "John", "email": "john@example.com"},
    dependencies=[Depends(add_bearer_token)]
)
async def create_user(resp: Response):
    """Создать нового пользователя."""
    return resp.json()
```

### Пример 2: Trace ID для трейсинга

Добавление уникального ID для отслеживания запросов:

```python
import uuid


async def add_trace_id(route, config):
    """Добавляет уникальный Trace ID для распределённого трейсинга."""
    trace_id = str(uuid.uuid4())
    config.setdefault("headers", {})["X-Trace-ID"] = trace_id
    
    # Также можно добавить в start_time для замера времени
    import time
    config["_start_time"] = time.time()
    
    return config


@app.get(
    url="https://api.example.com/data",
    dependencies=[Depends(add_trace_id)]
)
async def get_data(resp: Response):
    return resp.json()
```

### Пример 3: Несколько зависимостей

Зависимости выполняются по порядку, как в цепочке:

```python
async def add_auth(route, config):
    """Добавляет токен авторизации."""
    config.setdefault("headers", {})["Authorization"] = "Bearer token"
    return config


async def add_trace(route, config):
    """Добавляет Trace ID."""
    config.setdefault("headers", {})["X-Trace-ID"] = "123"
    return config


async def add_custom(route, config):
    """Добавляет кастомный заголовок."""
    config.setdefault("headers", {})["X-Custom-Header"] = "value"
    return config


@app.get(
    url="https://api.example.com/data",
    dependencies=[
        Depends(add_auth),      # Выполнится первым
        Depends(add_trace),     # Вторым
        Depends(add_custom),    # Третьим
    ]
)
async def handler(resp: Response):
    # Все заголовки будут добавлены в порядке
    return resp.json()
```

### Пример 4: Динамические заголовки на основе URL

Можно анализировать URL и добавлять разные заголовки:

```python
async def add_api_version(route, config):
    """Добавляет версию API в заголовки на основе URL."""
    headers = config.setdefault("headers", {})
    
    if "/v2/" in route.url:
        headers["X-API-Version"] = "v2"
        headers["Accept"] = "application/vnd.api.v2+json"
    else:
        headers["X-API-Version"] = "v1"
        headers["Accept"] = "application/json"
    
    return config


@app.get(
    url="https://api.example.com/v2/users",
    dependencies=[Depends(add_api_version)]
)
async def get_users_v2(resp: Response):
    return resp.json()


@app.get(
    url="https://api.example.com/v1/users",
    dependencies=[Depends(add_api_version)]
)
async def get_users_v1(resp: Response):
    return resp.json()
```

### Пример 5: Добавление query параметров

Зависимость может модифицировать query параметры:

```python
async def add_pagination(route, config):
    """Добавляет параметры пагинации по умолчанию."""
    route.params = route.params or {}
    route.params.setdefault("page", 1)
    route.params.setdefault("limit", 10)
    
    # Ограничим максимальный лимит
    if route.params.get("limit", 10) > 100:
        route.params["limit"] = 100
    
    return config


@app.get(
    url="https://api.example.com/users",
    params={"name": "John"},  # уже есть параметры
    dependencies=[Depends(add_pagination)]
)
async def get_users(resp: Response):
    # Фактический URL будет: /users?name=John&page=1&limit=10
    return resp.json()
```

### Пример 6: Логирование запросов

Простой способ логирования:

```python
import time


async def log_request(route, config):
    """Логирует информацию о запросе."""
    print(f"🚀 Отправка: {route.method} {route.url}")
    config["_start_time"] = time.time()
    return config


@app.get(
    url="https://api.example.com/data",
    dependencies=[Depends(log_request)]
)
async def handler(resp: Response):
    return resp.json()
```

### Пример 7: Условные заголовки

Добавление заголовков в зависимости от условий:

```python
async def add_conditional_headers(route, config):
    """Добавляет разные заголовки в зависимости от метода."""
    headers = config.setdefault("headers", {})
    
    if route.method == "POST":
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "application/json"
    elif route.method == "GET":
        headers["Accept"] = "application/json"
    
    return config


@app.post(
    url="https://api.example.com/data",
    json={"test": "value"},
    dependencies=[Depends(add_conditional_headers)]
)
async def create_data(resp: Response):
    return resp.json()
```

### Пример 8: Работа с кэшем

Использование use_cache для дорогих операций:

```python
import aiohttp


async def get_oauth_token(route, config):
    """Получает OAuth токен (дорогая операция)."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://auth.example.com/token",
            json={"client_id": "my_app", "client_secret": "secret"}
        ) as resp:
            data = await resp.json()
            token = data["access_token"]
    
    config.setdefault("headers", {})["Authorization"] = f"Bearer {token}"
    return config


# Токен получится один раз и будет использован для всех запросов
@app.get(
    url="https://api.example.com/users",
    dependencies=[Depends(get_oauth_token, use_cache=True)]
)
async def get_users(resp: Response):
    return resp.json()


@app.get(
    url="https://api.example.com/posts",
    dependencies=[Depends(get_oauth_token, use_cache=True)]
)
async def get_posts(resp: Response):
    return resp.json()
```

### Пример 9: Валидация перед запросом

Можно даже валидировать данные перед отправкой:

```python
async def validate_api_key(route, config):
    """Проверяет наличие API ключа."""
    api_key = config.get("headers", {}).get("X-API-Key")
    
    if not api_key:
        raise ValueError("API Key required")
    
    # Можно даже проверить валидность ключа
    if not is_valid_key(api_key):
        raise ValueError("Invalid API Key")
    
    return config


@app.get(
    url="https://api.example.com/data",
    get_request={"headers": {"X-API-Key": "my-key"}},
    dependencies=[Depends(validate_api_key)]
)
async def get_data(resp: Response):
    return resp.json()
```

## Использование Depends без скобок

Вы можете передавать функцию напрямую в Depends:

```python
async def add_auth(route, config):
    config.setdefault("headers", {})["Authorization"] = "Bearer token"
    return config


# Оба варианта работают одинаково
@app.get(url="/test1", dependencies=[Depends(add_auth)])
async def test1(resp): ...


@app.get(url="/test2", dependencies=[add_auth])  # Тоже самое!
async def test2(resp): ...
```

## Объединение с тегами

Зависимости отлично работают с тегами:

```python
async def add_auth(route, config):
    config.setdefault("headers", {})["Authorization"] = "Bearer token"
    return config


@app.get(
    url="https://api.example.com/users",
    tags=["users", "v1"],
    dependencies=[Depends(add_auth)]
)
async def get_users(resp): ...


@app.get(
    url="https://api.example.com/posts",
    tags=["posts", "v1"],
    dependencies=[Depends(add_auth)]
)
async def get_posts(resp): ...


# Запустить только пользователей
app.run(tags=["users"])
```

## Смотрите также

- [Middleware](middleware.md) — для глобальной логики
- [Конфигурация](configuration.md) — настройки по умолчанию
- [Быстрый старт](quick-start.md) — основы FastHTTP

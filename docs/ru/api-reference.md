# Справочник API

Полный справочник по всем классам, методам и опциям FastHTTP Client.

## Содержание

- [Класс FastHTTP](#класс-fasthttp)
- [Класс Response](#класс-response)
- [Класс Route](#класс-route)
- [Класс BaseMiddleware](#класс-basemiddleware)
- [Опции конфигурации](#опции-конфигурации)

## Класс FastHTTP

Основной класс для создания и управления HTTP запросами.

### Конструктор

```python
FastHTTP(
    debug: bool = False,
    get_request: dict | None = None,
    post_request: dict | None = None,
    put_request: dict | None = None,
    patch_request: dict | None = None,
    delete_request: dict | None = None,
) -> FastHTTP
```

#### Параметры

- `debug` (bool): Включить подробное логирование (по умолчанию: `False`)
- `middleware` (list[BaseMiddleware] | BaseMiddleware): Экземпляры middleware для применения ко всем запросам
- `get_request` (dict): Конфигурация по умолчанию для GET запросов
- `post_request` (dict): Конфигурация по умолчанию для POST запросов
- `put_request` (dict): Конфигурация по умолчанию для PUT запросов
- `patch_request` (dict): Конфигурация по умолчанию для PATCH запросов
- `delete_request` (dict): Конфигурация по умолчанию для DELETE запросов

#### Пример

```python
from fasthttp import FastHTTP

app = FastHTTP(
    debug=True,
    get_request={
        "headers": {"User-Agent": "MyApp/1.0"},
        "timeout": 10,
    },
    post_request={
        "headers": {"Content-Type": "application/json"},
        "timeout": 30,
    },
)
```

### Методы

#### `.get()`

Регистрирует GET запрос.

```python
def get(*, url: str, params: dict | None = None, response_model: type | None = None) -> Callable
```

**Параметры:**
- `url` (str): Целевой URL
- `params` (dict): Параметры запроса (опционально)
- `response_model` (type): Модель Pydantic для валидации ответа (опционально)

**Пример:**
```python
@app.get(url="https://api.example.com/users", params={"page": 1})
async def get_users(resp: Response):
    return resp.json()
```

#### `.post()`

Регистрирует POST запрос.

```python
def post(*, url: str, json: dict | None = None, data: dict | None = None, params: dict | None = None, response_model: type | None = None) -> Callable
```

**Параметры:**
- `url` (str): Целевой URL
- `json` (dict): JSON данные для отправки (опционально)
- `data` (dict): Данные формы для отправки (опционально)
- `params` (dict): Параметры запроса (опционально)
- `response_model` (type): Модель Pydantic для валидации ответа (опционально)

**Пример:**
```python
@app.post(url="https://api.example.com/users", json={"name": "John"})
async def create_user(resp: Response):
    return resp.status
```

#### `.put()`

Регистрирует PUT запрос.

```python
def put(*, url: str, json: dict | None = None, data: dict | None = None, params: dict | None = None, response_model: type | None = None) -> Callable
```

**Параметры:** Те же, что и у `.post()`

**Пример:**
```python
@app.put(url="https://api.example.com/users/1", json={"name": "Jane"})
async def update_user(resp: Response):
    return resp.status
```

#### `.patch()`

Регистрирует PATCH запрос.

```python
def patch(*, url: str, json: dict | None = None, data: dict | None = None, params: dict | None = None, response_model: type | None = None) -> Callable
```

**Параметры:** Те же, что и у `.post()`

**Пример:**
```python
@app.patch(url="https://api.example.com/users/1", json={"age": 25})
async def patch_user(resp: Response):
    return resp.status
```

#### `.delete()`

Регистрирует DELETE запрос.

```python
def delete(*, url: str, json: dict | None = None, data: dict | None = None, params: dict | None = None, response_model: type | None = None) -> Callable
```

**Параметры:** Те же, что и у `.post()`

**Пример:**
```python
@app.delete(url="https://api.example.com/users/1")
async def delete_user(resp: Response):
    return resp.status
```

#### `.run()`

Выполняет все зарегистрированные запросы.

```python
def run() -> None
```

**Пример:**
```python
if __name__ == "__main__":
    app.run()
```

## Класс Response

Представляет HTTP ответ с удобными методами доступа.

### Атрибуты

- `status` (int): HTTP код статуса
- `text` (str): Тело ответа в виде текста
- `headers` (dict): Заголовки ответа

### Методы

#### `.json()`

Парсит тело ответа как JSON.

```python
def json() -> JSONResponse.Value
```

**Возвращает:** Распарсенные JSON данные (dict, list, и т.д.)

**Пример:**
```python
@app.get(url="https://api.example.com/data")
async def handle_response(resp: Response):
    data = resp.json()
    return f"Получено {len(data)} элементов"
```

**Вызывает:** `json.JSONDecodeError` если ответ не является корректным JSON

#### `.__repr__()`

Строковое представление ответа.

```python
def __repr__() -> str
```

**Пример:**
```python
print(resp)  # <Response [200]>
```

## Класс Route

Внутренний класс, представляющий зарегистрированный маршрут. Обычно вы не взаимодействуете с ним напрямую.

### Атрибуты

- `method` (str): HTTP метод (GET, POST, и т.д.)
- `url` (str): Целевой URL
- `handler` (Callable): Функция-обработчик
- `params` (dict): Параметры запроса
- `json` (dict): JSON данные
- `data` (dict): Данные формы

## Класс BaseMiddleware

Базовый класс для создания middleware для перехвата и модификации HTTP запросов и ответов.

### Конструктор

```python
class BaseMiddleware:
    async def before_request(
        self, route: Route, config: RequestsOptinal
    ) -> RequestsOptinal:
        return config

    async def after_response(
        self, response: Response, route: Route, config: RequestsOptinal
    ) -> Response:
        return response

    async def on_error(
        self, error: Exception, route: Route, config: RequestsOptinal
    ) -> None:
        pass
```

### Методы

#### `.before_request()`

Вызывается перед отправкой HTTP запроса. Используйте этот метод для изменения конфигурации запроса.

```python
async def before_request(
    self, route: Route, config: RequestsOptinal
) -> RequestsOptinal
```

**Параметры:**
- `route` (Route): Выполняемый маршрут
- `config` (RequestsOptinal): Словарь конфигурации запроса

**Возвращает:** Измененная или исходная конфигурация запроса

**Пример:**
```python
class AuthMiddleware(BaseMiddleware):
    async def before_request(
        self, route: Route, config: RequestsOptinal
    ) -> RequestsOptinal:
        headers = config.get("headers", {})
        headers["Authorization"] = "Bearer token"
        config["headers"] = headers
        return config
```

#### `.after_response()`

Вызывается после получения успешного ответа. Используйте этот метод для изменения ответа.

```python
async def after_response(
    self, response: Response, route: Route, config: RequestsOptinal
) -> Response
```

**Параметры:**
- `response` (Response): Объект HTTP ответа
- `route` (Route): Маршрут, который был выполнен
- `config` (RequestsOptinal): Конфигурация запроса, которая была использована

**Возвращает:** Измененный или исходный объект ответа

**Пример:**
```python
class LoggingMiddleware(BaseMiddleware):
    async def after_response(
        self, response: Response, route: Route, config: RequestsOptinal
    ) -> Response:
        print(f"Ответ: {response.status}")
        return response
```

#### `.on_error()`

Вызывается при возникновении ошибки во время запроса.

```python
async def on_error(
    self, error: Exception, route: Route, config: RequestsOptinal
) -> None
```

**Параметры:**
- `error` (Exception): Исключение, которое произошло
- `route` (Route): Маршрут, который завершился ошибкой
- `config` (RequestsOptinal): Конфигурация запроса, которая была использована

**Возвращает:** None

**Пример:**
```python
class ErrorTrackingMiddleware(BaseMiddleware):
    async def on_error(
        self, error: Exception, route: Route, config: RequestsOptinal
    ) -> None:
        print(f"Ошибка: {error.__class__.__name__} на {route.url}")
```

### Использование Middleware

```python
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware

class MyMiddleware(BaseMiddleware):
    async def before_request(self, route, config):
        print(f"Запрос: {route.method} {route.url}")
        return config

# Один middleware
app = FastHTTP(middleware=MyMiddleware())

# Несколько middleware
app = FastHTTP(middleware=[
    AuthMiddleware(),
    LoggingMiddleware(),
    ErrorTrackingMiddleware()
])
```

Для получения подробной информации см. руководство [Middleware](middleware.md).

## Опции конфигурации

### Конфигурация запроса

Каждый тип запроса можно настроить с помощью:

```python
{
    "headers": {
        "User-Agent": "MyApp/1.0",
        "Authorization": "Bearer token",
        "Content-Type": "application/json",
    },
    "timeout": 30,  # Таймаут запроса в секундах
    "allow_redirects": True,
}
```

#### Заголовки

Пользовательские заголовки для запросов:

```python
app = FastHTTP(
    get_request={
        "headers": {
            "User-Agent": "MyApp/1.0",
            "X-Custom-Header": "value",
        }
    }
)
```

#### Таймаут

Таймаут запроса в секундах:

```python
app = FastHTTP(
    get_request={"timeout": 10}  # 10-секундный таймаут
)
```

### Глобальная vs По-запросная конфигурация

#### Глобальная конфигурация
```python
# Применяется ко всем GET запросам
app = FastHTTP(
    get_request={
        "headers": {"User-Agent": "Global/1.0"},
        "timeout": 5,
    }
)

@app.get(url="https://example.com")  # Использует глобальную конфигурацию
async def handler(resp: Response):
    return resp.status
```

#### Переопределение конкретного запроса
```python
# Переопределение конкретного запроса
@app.get(
    url="https://example.com",
    params={"custom": "param"}  # Дополнительные параметры
)
async def handler(resp: Response):
    return resp.status
```

## Логирование

### Уровни логирования

#### Уровень Info (по умолчанию)
Показывает базовую информацию о запросе/ответе:
```
16:09:18.955 │ INFO     │ fasthttp │ ✔ FastHTTP запущен
16:09:19.520 │ INFO     │ fasthttp │ ✔ ✔️ GET     https://api.example.com  200 458.26ms
```

#### Уровень Debug
Показывает подробную информацию включая заголовки и содержимое ответа:
```python
app = FastHTTP(debug=True)
```

Показывает:
- Заголовки запроса
- Заголовки ответа
- Тело ответа (сокращенное)
- Результаты обработчика

### Формат логирования

```
ВРЕМЯ       │ УРОВЕНЬ   │ ЛОГГЕР   │ СООБЩЕНИЕ
ЧЧ:ММ:СС.ммм │ DEBUG    │ fasthttp │ 🐛 Зарегистрирован маршрут: GET https://example.com
ЧЧ:ММ:СС.ммм │ INFO     │ fasthttp │ ✔ FastHTTP запущен
ЧЧ:ММ:СС.ммм │ DEBUG    │ fasthttp │ 🐛 → GET https://example.com | headers={...}
ЧЧ:ММ:СС.ммм │ INFO     │ fasthttp │ ✔ ← GET https://example.com [200] 123.45ms
ЧЧ:ММ:СС.ммм │ DEBUG    │ fasthttp │ ↳ {"key": "value"}
```

### Иконки

- 🐛 Уровень DEBUG
- ✔ Уровень INFO
- ⚠ Уровень WARNING
- ✖ Уровень ERROR
- 💀 Уровень CRITICAL

## 🔧 Обработка ошибок

FastHTTP предоставляет автоматическую обработку ошибок с красивым логированием.

### Автоматическая обработка ошибок

Все HTTP ошибки автоматически перехватываются и логируются:

```python
from fasthttp.exceptions import (
    FastHTTPConnectionError,
    FastHTTPTimeoutError, 
    FastHTTPBadStatusError,
    FastHTTPRequestError
)

# Ошибки автоматически логируются - не нужно их перехватывать!
@app.get(url="https://несуществующий.com/api")
async def test_handler(resp: Response):
    return resp.json()
```

**Автоматические типы ошибок:**

- `FastHTTPConnectionError` - Ошибки подключения
- `FastHTTPTimeoutError` - Таймауты запросов
- `FastHTTPBadStatusError` - HTTP коды статуса 4xx/5xx
- `FastHTTPRequestError` - Общие ошибки запросов

### Ручной вызов ошибок

Вы можете вручную вызывать эти исключения в ваших обработчиках:

```python
@app.get(url="https://api.example.com/data")
async def get_data(resp: Response):
    if resp.status == 404:
        raise FastHTTPBadStatusError(
            "Данные не найдены",
            url="https://api.example.com/data",
            status_code=404
        )
    return resp.json()
```

### Устаревший способ обработки ошибок (aiohttp)

Для продвинутых случаев использования вы можете по-прежнему использовать исключения aiohttp:

```python
try:
    app.run()
except aiohttp.ClientConnectionError as e:
    print(f"Ошибка подключения: {e}")
```

### Исключения обработчика
Исключения в функциях-обработчиках перехватываются и логируются:
```
16:09:20.037 │ ERROR    │ fasthttp │ Исключение обработчика в get_user: Ошибка декодирования JSON
```

## Советы по производительности

### Пакетные запросы
Зарегистрируйте несколько запросов и запустите их вместе:
```python
# Все запросы выполняются одновременно
@app.get(url="https://api1.com/data")
async def handler1(resp: Response): ...

@app.get(url="https://api2.com/data")
async def handler2(resp: Response): ...

@app.get(url="https://api3.com/data")
async def handler3(resp: Response): ...

app.run()  # Запускает все 3 запроса одновременно
```

### Задержки запросов
Небольшие задержки (0.5с) автоматически добавляются между запросами, чтобы не перегружать серверы.

### Асинхронная производительность
Построен на aiohttp для высокопроизводительных асинхронных операций.

---

*Больше примеров см. в [Примерах](examples.md)*

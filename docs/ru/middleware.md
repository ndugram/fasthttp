# Middleware

Middleware позволяет перехватывать и модифицировать HTTP запросы и ответы в FastHTTP. Это полезно для добавления аутентификации, логирования, обработки ошибок и других сквозных задач.

## Что такое Middleware?

Middleware - это класс, который подключается к жизненному циклу запроса. Вы можете использовать его для выполнения кода перед отправкой запроса, после получения ответа или при возникновении ошибки.

## Создание Middleware

Для создания middleware наследуйтесь от `BaseMiddleware` и переопределите нужные методы:

```python
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware
from fasthttp.response import Response
from fasthttp.routing import Route
from fasthttp.types import RequestsOptinal


class LoggingMiddleware(BaseMiddleware):
    async def before_request(
        self, route: Route, config: RequestsOptinal
    ) -> RequestsOptinal:
        print(f"Отправка {route.method} на {route.url}")
        return config

    async def after_response(
        self, response: Response, route: Route, config: RequestsOptinal
    ) -> Response:
        print(f"Получен ответ: {response.status}")
        return response


app = FastHTTP(middleware=[LoggingMiddleware()])


@app.get(url="https://httpbin.org/get")
async def get_data(resp: Response):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

## Методы Middleware

### before_request

Вызывается перед отправкой HTTP запроса. Используйте этот метод для изменения заголовков запроса, добавления аутентификации или логирования исходящих запросов.

```python
async def before_request(
    self, route: Route, config: RequestsOptinal
) -> RequestsOptinal:
    headers = config.get("headers", {})
    headers["Authorization"] = "Bearer token"
    config["headers"] = headers
    return config
```

### after_response

Вызывается после получения успешного ответа. Используйте этот метод для трансформации данных ответа, логирования метрик или кеширования ответов.

```python
async def after_response(
    self, response: Response, route: Route, config: RequestsOptinal
) -> Response:
    json_data = response.json()
    json_data["custom_field"] = "value"
    response.text = json.dumps(json_data)
    return response
```

### on_error

Вызывается при возникновении ошибки во время запроса. Используйте этот метод для кастомного логирования ошибок или отслеживания ошибок.

```python
async def on_error(
    self, error: Exception, route: Route, config: RequestsOptinal
) -> None:
    print(f"Ошибка на {route.url}: {error}")
```

## Использование нескольких Middleware

Вы можете использовать несколько экземпляров middleware. Они будут выполняться в том порядке, в котором вы их предоставили.

```python
app = FastHTTP(
    middleware=[
        AuthMiddleware(),
        LoggingMiddleware(),
        ErrorTrackingMiddleware()
    ]
)
```

## Типичные случаи использования

### Аутентификация

Добавление заголовков аутентификации ко всем запросам:

```python
class AuthMiddleware(BaseMiddleware):
    def __init__(self, token: str):
        self.token = token

    async def before_request(
        self, route: Route, config: RequestsOptinal
    ) -> RequestsOptinal:
        headers = config.get("headers", {})
        headers["Authorization"] = f"Bearer {self.token}"
        config["headers"] = headers
        return config
```

### Логирование

Логирование всех запросов и ответов:

```python
class LoggingMiddleware(BaseMiddleware):
    async def before_request(
        self, route: Route, config: RequestsOptinal
    ) -> RequestsOptinal:
        print(f"Запрос: {route.method} {route.url}")
        return config

    async def after_response(
        self, response: Response, route: Route, config: RequestsOptinal
    ) -> Response:
        print(f"Ответ: {response.status}")
        return response
```

### Отслеживание ошибок

Отслеживание и логирование ошибок:

```python
class ErrorTrackingMiddleware(BaseMiddleware):
    async def on_error(
        self, error: Exception, route: Route, config: RequestsOptinal
    ) -> None:
        print(f"Ошибка: {error.__class__.__name__} на {route.url}")
```

### ID запроса

Добавление уникальных идентификаторов запросов для трассировки:

```python
import uuid


class RequestIDMiddleware(BaseMiddleware):
    async def before_request(
        self, route: Route, config: RequestsOptinal
    ) -> RequestsOptinal:
        headers = config.get("headers", {})
        headers["X-Request-ID"] = str(uuid.uuid4())
        config["headers"] = headers
        return config
```

## Порядок выполнения Middleware

Middleware выполняется в порядке их предоставления:

1. Перед запросом: Middleware[0] -> Middleware[1] -> ... -> Middleware[n]
2. После ответа: Middleware[0] -> Middleware[1] -> ... -> Middleware[n]
3. При ошибке: Middleware[0] -> Middleware[1] -> ... -> Middleware[n]

Каждый middleware получает результат от предыдущего middleware, что позволяет связывать трансформации в цепочку.

## Лучшие практики

1. Оставляйте middleware сфокусированным на одной ответственности
2. Возвращайте измененный config или объект response
3. Обрабатывайте исключения в методах middleware
4. Используйте middleware для сквозных задач
5. Тестируйте middleware независимо

---

Для большего количества примеров см. раздел [Примеры](examples.md).

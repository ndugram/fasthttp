# Быстрый старт

Установка и первый запрос менее чем за 2 минуты.

## Как работает FastHTTP

Понимание архитектуры поможет использовать FastHTTP более эффективно.

### Поток выполнения

Когда вы вызываете `app.run()`, FastHTTP выполняет следующую последовательность:

```
1. Собирает все зарегистрированные маршруты (функции с @app.get, @app.post и т.д.)
         ↓
2. Проверяет, что каждый обработчик имеет аннотации типов (обязательно!)
         ↓
3. Создаёт асинхронные задачи для всех запросов
         ↓
4. Выполняет запросы параллельно с помощью asyncio
         ↓
5. Для каждого запроса:
   a. Применяет зависимости (модифицирует конфиг)
   b. Запускает middleware.before_request()
   c. Проверяет безопасность (SSRF и т.д.)
   d. Отправляет HTTP запрос через httpx
   e. Запускает middleware.after_response()
   f. Вызывает ваш обработчик с объектом Response
         ↓
6. Логирует результаты и завершается
```

### Основные понятия

- **Маршрут (Route)**: Функция, декорированная `@app.get()`, `@app.post()` и т.д. Определяет HTTP запрос.
- **Обработчик (Handler)**: Функция, которая обрабатывает ответ. Должна иметь аннотации типов.
- **Response**: Объект, содержащий ответ сервера (статус, тело, заголовки).
- **Зависимость (Dependency)**: Функция, которая модифицирует конфиг запроса перед отправкой.
- **Middleware**: Плагин, который может модифицировать запросы и ответы.

## Установка

Установите FastHTTP с помощью pip:

```bash
pip install fasthttp-client
```

Для HTTP/2 поддержки установите с дополнительными зависимостями:

```bash
pip install fasthttp-client[http2]
```

## Ваш первый запрос

Создайте файл `example.py`:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def main(resp: Response) -> dict:
    """Получает пост и возвращает JSON."""
    return resp.json()


if __name__ == "__main__":
    app.run()
```

:::tip Важно
Функции-обработчики должны иметь аннотацию возвращаемого типа (`-> dict`, `-> str`, `-> int` и т.д.). Это требование для корректной работы библиотеки.
:::

Запустите:

```bash
python example.py
```

Вывод:

```
INFO    │ fasthttp    │ ✔ FastHTTP started
INFO    │ fasthttp    │ ✔ Sending 1 requests
INFO    │ fasthttp    │ ✔ ✔ GET https://jsonplaceholder.typicode.com/posts/1 200 234.56ms
INFO    │ fasthttp    │ ✔ Done in 0.24s
```

## Подробнее о приложении

### Что делает FastHTTP?

FastHTTP — это асинхронный HTTP-клиент, похожий на FastAPI, но для исходящих запросов. Он позволяет:

- Определять HTTP-запросы как функции с декораторами
- Выполнять несколько запросов параллельно
- Добавлять зависимости (dependencies) для модификации запросов
- Использовать теги для фильтрации и группировки запросов
- Автоматически обрабатывать ошибки и логирование

### Структура приложения

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

# Создаём приложение
app = FastHTTP(debug=True)  # debug=True включает подробное логирование


# Определяем запрос с помощью декоратора
@app.get(url="https://api.example.com/data")
async def my_request(resp: Response) -> dict:
    # resp — объект ответа
    return resp.json()


# Запускаем
if __name__ == "__main__":
    app.run()
```

## HTTP методы

FastHTTP поддерживает все основные HTTP методы:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


# GET — получение данных
@app.get(url="https://api.example.com/users")
async def get_users(resp: Response):
    """Получить список пользователей."""
    return resp.json()


# POST — создание новых данных
@app.post(url="https://api.example.com/users", json={"name": "John", "email": "john@example.com"})
async def create_user(resp: Response):
    """Создать нового пользователя."""
    return resp.json()


# PUT — полное обновление данных
@app.put(url="https://api.example.com/users/1", json={"name": "Jane", "email": "jane@example.com"})
async def update_user(resp: Response):
    """Обновить пользователя полностью."""
    return resp.json()


# PATCH — частичное обновление данных
@app.patch(url="https://api.example.com/users/1", json={"age": 25})
async def patch_user(resp: Response):
    """Частично обновить пользователя."""
    return resp.json()


# DELETE — удаление данных
@app.delete(url="https://api.example.com/users/1")
async def delete_user(resp: Response):
    """Удалить пользователя."""
    return resp.status
```

## Параметры запроса

### Query параметры

Используйте параметр `params` для добавления query параметров:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.get(
    url="https://api.example.com/search",
    params={
        "q": "fasthttp",
        "page": 1,
        "limit": 10,
    }
)
async def search(resp: Response):
    """Поиск с пагинацией."""
    return resp.json()

# Фактический URL: https://api.example.com/search?q=fasthttp&page=1&limit=10
```

### JSON тело

Используйте параметр `json` для отправки JSON:

```python
@app.post(
    url="https://api.example.com/users",
    json={
        "name": "John",
        "email": "john@example.com",
        "age": 25,
    }
)
async def create_user(resp: Response):
    return resp.json()
```

### Raw данные

Используйте параметр `data` для отправки raw данных:

```python
@app.post(
    url="https://api.example.com/upload",
    data=b"raw bytes data",
)
async def upload(resp: Response):
    return resp.json()
```

### Заголовки

Добавьте заголовки с помощью параметра `get_request`:

```python
# Глобальные заголовки для всех запросов
app = FastHTTP(
    get_request={
        "headers": {
            "Authorization": "Bearer my-secret-token",
            "User-Agent": "MyApp/1.0",
            "Accept": "application/json",
        },
    },
)
```

Или локально для конкретного запроса:

```python
@app.get(
    url="https://api.example.com/data",
    get_request={
        "headers": {
            "X-Custom-Header": "value",
        }
    }
)
async def with_headers(resp: Response):
    return resp.json()
```

## Режим отладки

Включите режим отладки для просмотра подробной информации:

```python
app = FastHTTP(debug=True)
```

При `debug=True` вы увидите:
- Заголовки запроса и ответа
- Тело запроса и ответа
- Время выполнения каждого запроса
- Полный URL с параметрами

При `debug=False` (по умолчанию):
- Только статус и время выполнения

```python
app = FastHTTP(debug=False)  # Краткий вывод
```

## Обработка ошибок

FastHTTP автоматически обрабатывает ошибки и логирует их:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)


@app.get(url="https://httpbin.org/status/404")
async def handle_error(resp: Response):
    """Обрабатывает 404 ошибку."""
    return f"Статус: {resp.status}"


@app.get(url="https://httpbin.org/status/500")
async def handle_server_error(resp: Response):
    """Обрабатывает 500 ошибку."""
    return f"Статус: {resp.status}"
```

### Доступ к статусу и телу ответа

```python
@app.get(url="https://api.example.com/data")
async def handle_response(resp: Response):
    # Код статуса (200, 404, 500 и т.д.)
    status = resp.status
    
    # JSON тело
    data = resp.json()
    
    # Текстовый ответ
    text = resp.text
    
    # Заголовки ответа
    headers = resp.headers
    
    return {"status": status, "data": data}
```

## Параллельное выполнение

FastHTTP автоматически выполняет все зарегистрированные запросы параллельно с помощью библиотеки Python `asyncio`. Это означает, что если у вас есть несколько запросов, они все запустятся одновременно вместо последовательного выполнения, что значительно сокращает общее время выполнения.

### Как это работает

Когда вы вызываете `app.run()`, FastHTTP:

1. Собирает все зарегистрированные маршруты
2. Создаёт асинхронную задачу для каждого маршрута
3. Выполняет все задачи параллельно с помощью `asyncio.gather()`
4. Ожидает завершения всех запросов
5. Логирует результаты

### Пример

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def get_post(resp: Response):
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/users/1")
async def get_user(resp: Response):
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/comments/1")
async def get_comment(resp: Response):
    return resp.json()


if __name__ == "__main__":
    # Все три запроса выполнятся параллельно
    app.run()
```

### Последовательно vs Параллельно

**Последовательное выполнение** (если запросы идут друг за другом):
```
Запрос 1: 150мс
Запрос 2: 120мс  → начинается после запроса 1
Запрос 3: 110мс  → начинается после запроса 2
Всего: ~380мс
```

**Параллельное выполнение** (FastHTTP по умолчанию):
```
Запрос 1: 150мс ─┐
Запрос 2: 120мс ─┼─ Все выполняются одновременно
Запрос 3: 110мс ─┘
Всего: ~150мс (самый долгий запрос)
```

Вывод:

```
INFO    │ fasthttp    │ ✔ FastHTTP started
INFO    │ fasthttp    │ ✔ Sending 3 requests
INFO    │ fasthttp    │ ✔ ✔ GET https://jsonplaceholder.typicode.com/posts/1 200 150ms
INFO    │ fasthttp    │ ✔ ✔ GET https://jsonplaceholder.typicode.com/users/1 200 120ms
INFO    │ fasthttp    │ ✔ ✔ GET https://jsonplaceholder.typicode.com/comments/1 200 110ms
INFO    │ fasthttp    │ ✔ Done in 0.15s  # Все запросы параллельно!
```

### Один запрос

Если у вас только один запрос, он выполняется обычным образом:

```python
app = FastHTTP()


@app.get(url="https://api.example.com/data")
async def single_request(resp: Response):
    return resp.json()


app.run()  # Выполняет одиночный запрос
```

## Возвращаемые значения

Обработчик может возвращать разные типы данных:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


# Возврат словаря — автоматически преобразуется в JSON
@app.get(url="https://api.example.com/data")
async def return_dict(resp: Response):
    return {"message": "Hello", "status": resp.status}


# Возврат списка
@app.get(url="https://api.example.com/items")
async def return_list(resp: Response):
    return [1, 2, 3, 4, 5]


# Возврат строки
@app.get(url="https://api.example.com/text")
async def return_string(resp: Response):
    return "Hello, World!"


# Возврат числа (код статуса)
@app.get(url="https://api.example.com/status")
async def return_number(resp: Response):
    return resp.status


# Возврат Response объекта
@app.get(url="https://api.example.com/data")
async def return_response(resp: Response):
    return resp  # Вернёт весь объект ответа
```

## Теги

Теги позволяют группировать и фильтровать запросы:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.get(url="https://api.example.com/users", tags=["users"])
async def get_users(resp: Response) -> dict:
    return resp.json()


@app.post(url="https://api.example.com/users", tags=["users"])
async def create_user(resp: Response) -> dict:
    return resp.json()


@app.get(url="https://api.example.com/posts", tags=["posts"])
async def get_posts(resp: Response) -> dict:
    return resp.json()


# Запустить только пользователей
app.run(tags=["users"])
```

## Зависимости

Зависимости позволяют модифицировать запросы перед отправкой:

```python
from fasthttp import FastHTTP, Depends
from fasthttp.response import Response

app = FastHTTP()


async def add_auth(route, config):
    """Добавляет токен авторизации."""
    config.setdefault("headers", {})["Authorization"] = "Bearer my-token"
    return config


@app.get(
    url="https://api.example.com/protected",
    dependencies=[Depends(add_auth)]
)
async def protected_request(resp: Response):
    return resp.json()
```

Подробнее в разделе [Зависимости](dependencies.md).

## Валидация запросов

FastHTTP поддерживает валидацию данных запроса перед отправкой через Pydantic модели. Это позволяет убедиться, что данные корректны до того, как запрос уйдёт на сервер.

### Базовый пример

```python
from fasthttp import FastHTTP
from fasthttp.response import Response
from pydantic import BaseModel, Field

app = FastHTTP()

class UserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    age: int = Field(ge=0, le=150)

@app.post(
    url="https://api.example.com/users",
    json={"name": "John", "email": "john@example.com", "age": 25},
    request_model=UserRequest
)
async def create_user(resp: Response) -> dict:
    return resp.json()
```

Если данные не проходят валидацию, запрос не отправляется, а в логах появляется ошибка.

### Валидация с ошибкой

```python
@app.post(
    url="https://api.example.com/users",
    json={"name": "", "email": "invalid-email", "age": 200},
    request_model=UserRequest
)
async def create_user(resp: Response) -> dict:
    return resp.json()

# Запрос не пойдёт, в логах:
# ERROR | Request validation failed: ...
```

### Валидация с data

```python
class FormData(BaseModel):
    username: str
    password: str = Field(min_length=8)

@app.post(
    url="https://api.example.com/login",
    data={"username": "john", "password": "secret123"},
    request_model=FormData
)
async def login(resp: Response) -> dict:
    return resp.json()
```

Подробнее в разделе [Pydantic валидация](pydantic-validation.md).

## Lifespan

Lifespan позволяет выполнять код до и после всех запросов. Полезно для инициализации ресурсов (токенов, подключений) и очистки после выполнения.

### Базовый пример

```python
from contextlib import asynccontextmanager
from fasthttp import FastHTTP

@asynccontextmanager
async def lifespan(app: FastHTTP):
    # Startup — выполняется до запросов
    print("Starting up...")
    app.auth_token = "my-secret-token"  # Можно добавлять атрибуты к app

    yield  # Здесь выполняются запросы

    # Shutdown — выполняется после запросов
    print("Shutting down...")

app = FastHTTP(lifespan=lifespan)

@app.get(url="https://api.example.com/data")
async def get_data(resp: Response) -> dict:
    return resp.json()

app.run()
```

Вывод:

```
Starting up...
INFO    │ fasthttp    │ ✔ FastHTTP started
INFO    │ fasthttp    │ ✔ Sending 1 requests
INFO    │ fasthttp    │ ✔ ✔ GET https://api.example.com/data 200 150ms
INFO    │ fasthttp    │ ✔ Done in 0.15s
Shutting down...
```

### Примеры использования

**Загрузка токена авторизации:**

```python
import os
from contextlib import asynccontextmanager
from fasthttp import FastHTTP

@asynccontextmanager
async def lifespan(app: FastHTTP):
    # Загрузить токен из переменной окружения или файла
    app.api_token = os.getenv("API_TOKEN") or await load_token_from_file()
    yield

app = FastHTTP(lifespan=lifespan)
```

**Подключение к внешним сервисам:**

```python
from contextlib import asynccontextmanager
from fasthttp import FastHTTP
import aioredis

@asynccontextmanager
async def lifespan(app: FastHTTP):
    # Startup — подключиться к Redis
    app.redis = await aioredis.from_url("redis://localhost")
    print("Redis connected")

    yield

    # Shutdown — закрыть соединение
    await app.redis.close()
    print("Redis disconnected")

app = FastHTTP(lifespan=lifespan)
```

**Сбор статистики:**

```python
from contextlib import asynccontextmanager
from fasthttp import FastHTTP

@asynccontextmanager
async def lifespan(app: FastHTTP):
    # Инициализация счётчиков
    app.request_count = 0
    app.total_time = 0.0

    yield

    # Вывести статистику после выполнения
    print(f"Total requests: {app.request_count}")
    print(f"Total time: {app.total_time:.2f}s")

app = FastHTTP(lifespan=lifespan)
```

### Без lifespan

Если `lifespan` не указан, приложение работает как раньше:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()  # Без lifespan

@app.get(url="https://api.example.com/data")
async def get_data(resp: Response) -> dict:
    return resp.json()

app.run()
```

## Следующие шаги

Теперь вы знаете основы. Дальше изучите:

- [Конфигурация](configuration.md) — подробнее о настройках
- [Зависимости](dependencies.md) — модификация запросов
- [Middleware](middleware.md) — глобальная логика
- [CLI](cli.md) — командная строка
- [Справочник API](api-reference.md) — полная документация

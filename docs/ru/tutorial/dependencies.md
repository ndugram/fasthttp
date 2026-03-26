# Зависимости

Зависимости позволяют модифицировать запросы перед отправкой.

## Что такое зависимости

Зависимость - это функция, которая выполняется перед каждым запросом и может модифицировать конфигурацию запроса. Это полезно для:

- Добавления заголовков авторизации
- Добавления trace ID
- Модификации параметров запроса
- Логирования

## Базовый пример

```python
from fasthttp import FastHTTP, Depends
from fasthttp.response import Response

app = FastHTTP()


async def add_auth(route, config):
    config.setdefault("headers", {})["Authorization"] = "Bearer my-token"
    return config


@app.get(
    url="https://api.example.com/protected",
    dependencies=[Depends(add_auth)]
)
async def protected_request(resp: Response) -> dict:
    return resp.json()
```

## Сигнатура функции зависимости

Функция зависимости принимает два параметра:

```python
async def my_dependency(route, config):
    # route - информация о запросе
    # config - конфигурация запроса
    
    # Модифицируем config
    config["headers"]["X-Custom"] = "value"
    
    # Возвращаем модифицированный config
    return config
```

### Атрибуты route

```python
route.method      # HTTP метод: "GET", "POST" и т.д.
route.url         # Полный URL запроса
route.params      # Query параметры
route.json        # JSON тело
route.data        # Сырые данные
route.tags        # Теги запроса
```

### Ключи config

```python
config.get("headers", {})      # Заголовки запроса
config.get("timeout", 30.0)    # Таймаут в секундах
config.get("allow_redirects", True)
```

## Несколько зависимостей

Зависимости выполняются по порядку:

```python
async def add_auth(route, config):
    config.setdefault("headers", {})["Authorization"] = "Bearer token"
    return config


async def add_trace(route, config):
    config.setdefault("headers", {})["X-Trace-ID"] = "123"
    return config


@app.get(
    url="https://api.example.com/data",
    dependencies=[Depends(add_auth), Depends(add_trace)]
)
async def handler(resp: Response) -> dict:
    return resp.json()
```

## Использование кэша

Используйте `use_cache` для кэширования дорогих операций:

```python
async def get_token(route, config):
    token = await fetch_token()
    config["headers"]["Authorization"] = f"Bearer {token}"
    return config


# Токен получится один раз и будет использован повторно
@app.get(url="/api/data", dependencies=[Depends(get_token, use_cache=True)])
async def handler1(resp): ...


@app.get(url="/api/other", dependencies=[Depends(get_token, use_cache=True)])
async def handler2(resp): ...
```

## Сравнение с Middleware

| Функция | Middleware | Зависимости |
|---------|------------|-------------|
| Глобальное применение | Да | Нет |
| Конкретный запрос | Нет | Да |
| Может модифицировать ответ | Да | Нет |
| Проще в использовании | Нет | Да |

# FastHTTP

Асинхронный HTTP-клиент для Python с декларативным подходом, похожий на FastAPI.

## Особенности

- **Декларативный стиль** — определяйте запросы как функции с декораторами
- **Асинхронность** — параллельное выполнение запросов с asyncio
- **Зависимости** — модификация запросов перед отправкой
- **Теги** — группировка и фильтрация запросов
- **Middleware** — глобальная логика для всех запросов
- **Pydantic** — валидация ответов
- **HTTP/2** — поддержка современного протокола
- **CLI** — удобная командная строка

## Установка

```bash
pip install fasthttp-client
```

Для HTTP/2:

```bash
pip install fasthttp-client[http2]
```


## Быстрый пример

```python
from fasthttp import FastHTTP

app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def main(resp):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

## Зачем нужен FastHTTP?

### Проблема

Обычно при работе с HTTP запросами в Python:

```python
# Много boilerplate кода
import aiohttp

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.example.com/data") as resp:
            data = await resp.json()
            # ... обработка
```

### Решение с FastHTTP

```python
# Чистый и понятный код
from fasthttp import FastHTTP

app = FastHTTP()

@app.get(url="https://api.example.com/data")
async def main(resp):
    return resp.json()
```

## Документация

### Основы

- [Быстрый старт](quick-start.md) — начните здесь
- [Конфигурация](configuration.md) — настройки приложения
- [CLI](cli.md) — командная строка

### Продвинутые темы

- [Зависимости](dependencies.md) — модификация запросов
- [Middleware](middleware.md) — глобальная логика
- [Pydantic](pydantic-validation.md) — валидация
- [HTTP/2](http2-support.md) — поддержка HTTP/2

### Дополнительно

- [Примеры](examples.md) — больше примеров кода
- [API Reference](api-reference.md) — полная документация

## Сравнение с другими библиотеками

| Библиотека | Стиль | Async | Зависимости |
|------------|-------|-------|-------------|
| **FastHTTP** | Декларативный | ✅ Да | ✅ Да |
| requests | Императивный | ❌ Нет | ❌ Нет |
| aiohttp | Императивный | ✅ Да | ❌ Нет |
| httpx | Императивный | ✅ Да | ❌ Нет |

## Примеры использования

### Несколько запросов параллельно

```python
from fasthttp import FastHTTP

app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def get_post(resp):
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/users/1")
async def get_user(resp):
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/comments/1")
async def get_comment(resp):
    return resp.json()


# Все три запроса выполнятся параллельно!
if __name__ == "__main__":
    app.run()
```

### С тегами

```python
from fasthttp import FastHTTP

app = FastHTTP()


@app.get(url="https://api.example.com/users", tags=["users"])
async def get_users(resp):
    return resp.json()


@app.get(url="https://api.example.com/posts", tags=["posts"])
async def get_posts(resp):
    return resp.json()


# Запустить только пользователей
app.run(tags=["users"])
```

### С зависимостями

```python
from fasthttp import FastHTTP, Depends

app = FastHTTP()


async def add_auth(route, config):
    config.setdefault("headers", {})["Authorization"] = "Bearer token"
    return config


@app.get(
    url="https://api.example.com/data",
    dependencies=[Depends(add_auth)]
)
async def protected(resp):
    return resp.json()
```

## Сообщество

- GitHub: https://github.com/your-repo/fasthttp
- PyPI: https://pypi.org/project/fasthttp-client/

## Лицензия

MIT License

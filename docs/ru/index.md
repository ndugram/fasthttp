# FastHTTP Client

Быстрый и простой HTTP-клиент с поддержкой async и красивым логированием.

[![PyPI Version](https://img.shields.io/pypi/v/fasthttp-client?style=flat&label=PyPI)](https://pypi.org/project/fasthttp-client/)
[![Python Versions](https://img.shields.io/pypi/pyversions/fasthttp-client?style=flat)](https://pypi.org/project/fasthttp-client/)
[![License](https://img.shields.io/pypi/l/fasthttp-client?style=flat)](https://github.com/ndugram/fasthttp)
[![Downloads](https://img.shields.io/pypi/dm/fasthttp-client?style=flat)](https://pypi.org/project/fasthttp-client/)

---

## Особенности

| | |
|:---|:---|
| **Декларативный стиль** | Определяйте запросы как функции с декораторами |
| **Асинхронность** | Параллельное выполнение запросов с asyncio |
| **Зависимости** | Модификация запросов перед отправкой |
| **Теги** | Группировка и фильтрация запросов |
| **Middleware** | Глобальная логика для всех запросов |
| **Pydantic** | Валидация ответов |
| **HTTP/2** | Поддержка современного протокола |
| **CLI** | Удобная командная строка |

---

## Установка

```bash
pip install fasthttp-client
```

Для HTTP/2:

```bash
pip install fasthttp-client[http2]
```

---

## Быстрый пример

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def main(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()
```

!!! tip "Важно"
    Функции-обработчики должны иметь аннотацию возвращаемого типа (`-> dict`, `-> str`, `-> int` и т.д.)

---

## Документация

### Основы

- [Быстрый старт](quick-start.md) - Начните здесь
- [Конфигурация](configuration.md) - Настройки приложения
- [CLI](cli.md) - Командная строка

### Продвинутые темы

- [Зависимости](dependencies.md) - Модификация запросов
- [Middleware](middleware.md) - Глобальная логика
- [GraphQL](graphql.md) - Поддержка GraphQL
- [Pydantic](pydantic-validation.md) - Валидация
- [HTTP/2](http2-support.md) - Поддержка HTTP/2
- [Безопасность](security.md) - Встроенная защита

### Дополнительно

- [Примеры](examples.md) - Больше примеров кода
- [API Reference](api-reference.md) - Полная документация

---

## Зачем нужен FastHTTP?

### Проблема

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
from fasthttp.response import Response

app = FastHTTP()


@app.get(url="https://api.example.com/data")
async def main(resp: Response) -> dict:
    return resp.json()
```

---

## Сравнение

| Функция | FastHTTP | requests | aiohttp | httpx |
|:---|:---:|:---:|:---:|:---:|
| Декларативный | Да | Нет | Нет | Нет |
| Async | Да | Нет | Да | Да |
| Зависимости | Да | Нет | Нет | Нет |
| Теги | Да | Нет | Нет | Нет |
| Middleware | Да | Нет | Нет | Нет |
| Pydantic | Да | Нет | Нет | Нет |
| HTTP/2 | Да | Нет | Нет | Да |
| CLI | Да | Нет | Нет | Нет |

---

## Ссылки

- [Документация](https://fasthttp.ndugram.dev) - Английская версия
- [GitHub](https://github.com/ndugram/fasthttp) - Репозиторий
- [PyPI](https://pypi.org/project/fasthttp-client/) - Скачать библиотеку

---

## Язык

- [English Documentation](../en/index.md)
- [Русская документация](index.md)

---

## Лицензия

MIT License

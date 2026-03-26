# О проекте

Информация о FastHTTP.

## Что такое FastHTTP?

FastHTTP - это легковесный асинхронный HTTP-клиент, построенный на базе httpx. Он предоставляет чистый декларативный API для определения HTTP запросов и обработки ответов.

## Возможности

- Декларативный стиль - определение запросов как функций с декораторами
- Асинхронная поддержка - параллельное выполнение запросов с asyncio
- Зависимости - модификация запросов перед отправкой
- Теги - группировка и фильтрация запросов
- Middleware - глобальная логика для всех запросов
- Pydantic - валидация ответов
- HTTP/2 - поддержка современного протокола
- CLI - удобный интерфейс командной строки
- Встроенная безопасность - защита SSRF, circuit breaker

## Почему FastHTTP?

Традиционные HTTP-клиенты требуют многословного кода:

```python
# Много boilerplate кода
import aiohttp

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.example.com/data") as resp:
            data = await resp.json()
```

FastHTTP упрощает это:

```python
# Чисто и просто
from fasthttp import FastHTTP

app = FastHTTP()

@app.get(url="https://api.example.com/data")
async def main(resp):
    return resp.json()
```

## Лицензия

MIT License

## GitHub

https://github.com/ndugram/fasthttp

## Документация

https://fasthttp.ndugram.dev

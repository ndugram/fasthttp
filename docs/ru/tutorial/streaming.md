# Стриминг

`AsyncSession.stream()` — это async context manager для потоковых HTTP-ответов: chunked transfer, Server-Sent Events (SSE), и любые ответы, которые нужно обрабатывать по мере поступления данных, не дожидаясь полного тела.

## Когда использовать стриминг

| | `session.get()` / `session.post()` | `session.stream()` |
|---|---|---|
| Ждёт | Всё тело целиком | Первый байт |
| Память | Всё тело в RAM | Чанк за чанком |
| Когда | Обычные JSON / REST API | SSE, токены ИИ, большие файлы, live-логи |

Используйте `session.stream()` когда:
- Получаете Server-Sent Events (API языковых моделей, live-фиды)
- Скачиваете большие файлы без буферизации
- Обрабатываете ответ построчно по мере поступления

## Базовое использование

```python
import asyncio
from fasthttp import AsyncSession


async def main():
    async with AsyncSession(security=False) as session:
        async with session.stream("GET", "https://httpbin.org/stream/5") as resp:
            async for line in resp.aiter_lines():
                print(line)


asyncio.run(main())
```

## Сигнатура

```python
session.stream(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    content: bytes | None = None,
    timeout: float | None = None,
)
```

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `method` | `str` | — | HTTP метод: `"GET"`, `"POST"` и т.д. |
| `url` | `str` | — | URL или относительный путь (разрешается через `base_url`) |
| `headers` | `dict` | `None` | Заголовки запроса, мержатся поверх заголовков сессии |
| `content` | `bytes` | `None` | Сырое байтовое тело (JSON-payload, бинарные данные) |
| `timeout` | `float` | дефолт сессии | Переопределить таймаут в секундах |

Context manager возвращает `httpx.Response` в режиме стриминга. Итерировать можно через:

- `resp.aiter_lines()` — построчно (убирает `\n`)
- `resp.aiter_bytes(chunk_size)` — сырые байтовые чанки
- `resp.aiter_text()` — декодированные текстовые чанки
- `await resp.aread()` — прочитать всё тело сразу

## Server-Sent Events (SSE)

SSE передаёт строки `data: ...`, разделённые пустыми строками. Типичный паттерн для AI API:

```python
import asyncio
import json
from fasthttp import AsyncSession


async def main():
    payload = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "Привет!"}],
        "stream": True,
    }).encode()

    async with AsyncSession(security=False, timeout=60.0) as session:
        async with session.stream(
            "POST",
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": "Bearer YOUR_API_KEY",
                "Content-Type": "application/json",
            },
            content=payload,
        ) as resp:
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data = line[6:]
                if data == "[DONE]":
                    break
                chunk = json.loads(data)
                token = chunk["choices"][0]["delta"].get("content", "")
                print(token, end="", flush=True)


asyncio.run(main())
```

## Сырое байтовое тело

Передавайте любой сериализованный payload через `content=`:

```python
import asyncio
import json
from fasthttp import AsyncSession


async def main():
    body = json.dumps({"query": "stream this"}).encode()

    async with AsyncSession(
        base_url="https://api.example.com",
        headers={"Authorization": "Bearer token"},
        security=False,
    ) as session:
        async with session.stream("POST", "/stream", content=body) as resp:
            async for chunk in resp.aiter_bytes(1024):
                process(chunk)


asyncio.run(main())
```

## Скачивание больших файлов

Читайте чанками, чтобы не загружать весь файл в память:

```python
import asyncio
from fasthttp import AsyncSession


async def download(url: str, dest: str) -> None:
    async with AsyncSession(security=False, timeout=300.0) as session:
        async with session.stream("GET", url) as resp:
            with open(dest, "wb") as f:
                async for chunk in resp.aiter_bytes(8192):
                    f.write(chunk)


asyncio.run(download("https://example.com/large-file.zip", "file.zip"))
```

## Заголовки сессии при стриминге

Заголовки сессии автоматически мержатся в каждый вызов `stream()`:

```python
import asyncio
from fasthttp import AsyncSession


async def main():
    async with AsyncSession(
        base_url="https://api.example.com",
        headers={"Authorization": "Bearer token"},
        security=False,
    ) as session:
        # Заголовок Authorization включается автоматически
        async with session.stream("GET", "/events") as resp:
            async for line in resp.aiter_lines():
                print(line)


asyncio.run(main())
```

Заголовки запроса **мержатся поверх** заголовков сессии — они их не заменяют.

## Проверка статуса перед чтением

Проверьте статус до итерации тела:

```python
import asyncio
from fasthttp import AsyncSession


async def main():
    async with AsyncSession(security=False) as session:
        async with session.stream("GET", "https://httpbin.org/stream/3") as resp:
            if resp.status_code != 200:
                print(f"Ошибка: {resp.status_code}")
                return
            async for line in resp.aiter_lines():
                print(line)


asyncio.run(main())
```

## Импорт

```python
from fasthttp import AsyncSession
# или
from fasthttp.session import AsyncSession
```

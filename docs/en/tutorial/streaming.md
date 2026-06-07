# Streaming

`AsyncSession.stream()` is an async context manager for streaming HTTP responses — chunked transfers, Server-Sent Events (SSE), and any response where you want to process data as it arrives instead of waiting for the full body.

## When to Use Streaming

| | `session.get()` / `session.post()` | `session.stream()` |
|---|---|---|
| Waits for | Full response body | First byte |
| Memory | Entire body in RAM | Chunk at a time |
| Use case | Normal JSON / REST APIs | SSE, AI tokens, large files, live logs |

Use `session.stream()` when:
- Receiving Server-Sent Events (LLM APIs, live feeds)
- Downloading large files without buffering
- Processing responses line-by-line as they arrive

## Basic Usage

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

## Signature

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

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `method` | `str` | — | HTTP method: `"GET"`, `"POST"`, etc. |
| `url` | `str` | — | URL or relative path (resolved against `base_url`) |
| `headers` | `dict` | `None` | Per-request headers, merged on top of session headers |
| `content` | `bytes` | `None` | Raw bytes body (use for JSON payloads, binary data) |
| `timeout` | `float` | session default | Override timeout in seconds |

The context manager yields an `httpx.Response` in streaming mode. You can iterate it with:

- `resp.aiter_lines()` — line by line (strips `\n`)
- `resp.aiter_bytes(chunk_size)` — raw byte chunks
- `resp.aiter_text()` — decoded text chunks
- `await resp.aread()` — read the full body at once

## Server-Sent Events (SSE)

SSE streams `data: ...` lines terminated by blank lines. A common pattern used with AI APIs:

```python
import asyncio
import json
from fasthttp import AsyncSession


async def main():
    payload = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "Hello!"}],
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

## Raw Bytes Body

Pass any serialized payload via `content=`:

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

## Downloading Large Files

Read in chunks to avoid loading the entire file into memory:

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

## Session Headers with Streaming

Headers set on the session are automatically merged into every `stream()` call:

```python
import asyncio
from fasthttp import AsyncSession


async def main():
    async with AsyncSession(
        base_url="https://api.example.com",
        headers={"Authorization": "Bearer token"},
        security=False,
    ) as session:
        # Authorization header is included automatically
        async with session.stream("GET", "/events") as resp:
            async for line in resp.aiter_lines():
                print(line)


asyncio.run(main())
```

Per-request `headers` are **merged on top** of session headers — they do not replace them.

## Checking Status Before Reading

Inspect the status code before iterating the body:

```python
import asyncio
from fasthttp import AsyncSession


async def main():
    async with AsyncSession(security=False) as session:
        async with session.stream("GET", "https://httpbin.org/stream/3") as resp:
            if resp.status_code != 200:
                print(f"Error: {resp.status_code}")
                return
            async for line in resp.aiter_lines():
                print(line)


asyncio.run(main())
```

## Import

```python
from fasthttp import AsyncSession
# or
from fasthttp.session import AsyncSession
```

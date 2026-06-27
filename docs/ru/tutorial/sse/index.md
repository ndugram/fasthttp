# Server-Sent Events (SSE)

FastHTTP поддерживает **Server-Sent Events (SSE)** — однонаправленный протокол «толкающих» уведомлений поверх обычного HTTP, где сервер стримит события по мере их возникновения.

SSE-роуты определяются через декоратор `@app.sse()`. Хэндлер вызывается на каждое событие и получает объект [`SSEEvent`][sse-event].

---

## Быстрый старт

Подключитесь к публичному SSE-потоку Wikimedia и печатайте каждое событие:

```python
from fasthttp import FastHTTP, SSEEvent

app = FastHTTP()


@app.sse(url="https://stream.wikimedia.org/v2/stream/recentchange")
async def watch_wikipedia(event: SSEEvent) -> None:
    import json
    data = json.loads(event.data)
    print(f"[{event.event}] {data['title']}")


if __name__ == "__main__":
    app.run()
```

Запустите:

```bash
python main.py
```

Вывод:

```
INFO     | fasthttp    | FastHTTP started
INFO     | fasthttp    | Running 1 routes
INFO     | fasthttp    | SSE streams: 1
INFO     | fasthttp    | SSE connecting: https://stream.wikimedia.org/v2/stream/recentchange
INFO     | fasthttp    | SSE connected: https://stream.wikimedia.org/v2/stream/recentchange
[message] Frank Sinatra
[message] Python (programming language)
[message] List of mountains by elevation
^C  INFO     | fasthttp    | Interrupted by user
```

Нажмите **Ctrl+C** для остановки.

---

## Сигнатура `@app.sse()`

```python
@app.sse(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    reconnect: bool = False,
    max_retries: int = 0,
    tags: list[str] | None = None,
)
```

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `url` | `str` | — | URL SSE-эндпоинта (`http://` или `https://`). |
| `headers` | `dict[str, str]` | `None` | Дополнительные заголовки запроса. |
| `reconnect` | `bool` | `False` | Автопереподключение при разрыве. |
| `max_retries` | `int` | `0` | Максимум попыток переподключения. `-1` = безлимит. |
| `tags` | `list[str]` | `None` | Теги для группировки и фильтрации. |

---

## Объект `SSEEvent`

Каждое событие содержит:

| Поле | Тип | Описание |
|------|-----|----------|
| `event` | `str` | Тип события (по умолчанию `"message"`). |
| `data` | `str` | Тело события в виде строки. |
| `id` | `str \| None` | ID события для отслеживания переподключения (`Last-Event-ID`). |
| `retry` | `int \| None` | Время переподключения в мс (от сервера). |

```python
@app.sse(url="https://api.example.com/events")
async def handle(event: SSEEvent) -> None:
    print(f"Тип: {event.event}")       # "update", "alert", ...
    print(f"Данные: {event.data}")      # payload
    print(f"ID:   {event.id}")          # для переподключения
```

---

## Пользовательские заголовки

Передавайте `headers` для аутентификации или кастомного User-Agent:

```python
@app.sse(
    url="https://api.example.com/events",
    headers={
        "Authorization": "Bearer your-token",
        "User-Agent": "MyApp/1.0",
    },
)
async def handle(event: SSEEvent) -> None:
    print(event.data)
```

---

## Автопереподключение

При `reconnect=True` FastHTTP переподключается с экспоненциальной задержкой (`2^attempt` секунд, не более 30с). Заголовок `Last-Event-ID` отправляется автоматически — сервер может продолжить с последнего полученного события.

```python
@app.sse(
    url="https://api.example.com/events",
    reconnect=True,
    max_retries=10,
)
async def handle(event: SSEEvent) -> None:
    print(event.data)
```

Установите `max_retries=-1` для безлимитных попыток.

---

## Совместная работа с HTTP

SSE-потоки выполняются вместе с HTTP-запросами и WebSocket-соединениями. HTTP завершается первым, затем приложение остаётся активным до завершения SSE-потоков или Ctrl+C.

```python
from fasthttp import FastHTTP, SSEEvent
from fasthttp.response import Response

app = FastHTTP()


@app.get(url="https://api.example.com/status")
async def health(resp: Response) -> dict:
    return resp.json()


@app.sse(url="https://stream.wikimedia.org/v2/stream/recentchange")
async def watch(event: SSEEvent) -> None:
    print(event.data)


if __name__ == "__main__":
    app.run()  # HTTP выполняется первым, SSE остаётся активным до Ctrl+C
```

---

## Локальная разработка

Для тестирования без удалённого сервера запустите встроенный пример с локальным SSE-сервером:

```bash
python examples/sse/local_server.py
```

---

## SSE vs WebSocket

| Возможность | SSE | WebSocket |
|-------------|-----|-----------|
| Направление | Сервер → Клиент | Двустороннее |
| Протокол | Обычный HTTP | WS / WSS |
| Формат | Только текст (`data:` строки) | Текст + Бинарные |
| Автопереподключение | Встроено | Вручную |
| Сценарии | Ленты событий, уведомления, AI-токены | Чат, игры, совместная работа |

Используйте SSE если нужно только **получать** события от сервера. Используйте WebSocket если нужно ещё и **отправлять** данные обратно.

[sse-event]: ../../reference/fasthttp.md#fasthttp.sse.SSEEvent

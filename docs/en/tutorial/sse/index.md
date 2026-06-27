# Server-Sent Events (SSE)

FastHTTP supports **Server-Sent Events (SSE)** — a one-way push protocol over plain HTTP where the server streams events to the client as they happen.

SSE routes are defined with the `@app.sse()` decorator. The handler is called once per event and receives an [`SSEEvent`][sse-event] object.

---

## Quick Start

Connect to a public SSE stream and print each event:

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

Run it:

```bash
python main.py
```

Output:

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

Press **Ctrl+C** to stop.

---

## `@app.sse()` Signature

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

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `str` | — | SSE endpoint URL (`http://` or `https://`). |
| `headers` | `dict[str, str]` | `None` | Extra headers sent with the connection request. |
| `reconnect` | `bool` | `False` | Automatically reconnect when the connection drops. |
| `max_retries` | `int` | `0` | Max reconnect attempts (ignored when `reconnect=False`). `-1` = unlimited. |
| `tags` | `list[str]` | `None` | Tags for grouping and filtering routes. |

---

## The `SSEEvent` Object

Every event carries these fields:

| Field | Type | Description |
|-------|------|-------------|
| `event` | `str` | Event type from the server (`"message"` by default). |
| `data` | `str` | The event payload as a string. |
| `id` | `str \| None` | Event ID used for reconnection tracking (`Last-Event-ID`). |
| `retry` | `int \| None` | Reconnection time in milliseconds suggested by the server. |

```python
@app.sse(url="https://api.example.com/events")
async def handle(event: SSEEvent) -> None:
    print(f"Type: {event.event}")      # "update", "alert", ...
    print(f"Data: {event.data}")       # the payload
    print(f"ID:   {event.id}")         # for reconnection
```

---

## Custom Headers

Pass `headers` for authentication or custom User-Agent:

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

## Auto-Reconnect

When `reconnect=True`, FastHTTP reconnects with exponential backoff (`2^attempt` seconds, capped at 30s) if the connection drops. The `Last-Event-ID` header is sent automatically so the server can resume from where you left off.

```python
@app.sse(
    url="https://api.example.com/events",
    reconnect=True,
    max_retries=10,
)
async def handle(event: SSEEvent) -> None:
    print(event.data)
```

Set `max_retries=-1` for unlimited reconnection attempts.

---

## Running with HTTP Routes

SSE streams run alongside HTTP requests and WebSocket connections. HTTP requests complete first, then the app stays alive until all SSE streams are done or interrupted.

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
    app.run()  # HTTP completes first, then SSE stays alive until Ctrl+C
```

---

## Local Development

For testing without a remote server, create a local SSE server. See the [`examples/sse/local_server.py`](https://github.com/ndugram/fasthttp/blob/master/examples/sse/local_server.py) for a complete self-contained example.

```bash
python examples/sse/local_server.py
```

---

## SSE vs WebSocket

| Feature | SSE | WebSocket |
|---------|-----|-----------|
| Direction | Server → Client | Bidirectional |
| Protocol | Plain HTTP | WS / WSS |
| Message format | Text only (`data:` lines) | Text + Binary |
| Auto-reconnect | Built-in (browsers) / via `reconnect=True` | Manual |
| Use case | Live feeds, notifications, AI token streaming | Chat, gaming, real-time collaboration |

Use SSE when you only need to **receive** events from a server. Use WebSocket when you also need to **send** data back.

[sse-event]: ../../reference/fasthttp.md#fasthttp.sse.SSEEvent

# WebSocket

FastHTTP supports **WebSocket** connections for real-time bidirectional communication.

WebSocket routes are defined with the `@app.ws()` decorator — same declarative style as HTTP routes, but the handler receives a `WebSocket` connection object instead of a [`Response`](../../reference/response.md).

---

## Quick Start

Connect to a WebSocket echo server, send a message, and print the response:

```python
from fasthttp import FastHTTP, WebSocket

app = FastHTTP()


@app.ws(url="wss://echo.websocket.org")
async def echo(ws: WebSocket) -> None:
    await ws.send("Hello from fasthttp!")
    msg = await ws.recv()
    print(f"Received: {msg}")


if __name__ == "__main__":
    app.run()
```

Run it:

```bash
python main.py
```

Output:

```
INFO    | fasthttp    | FastHTTP started
INFO    | fasthttp    | Running 1 routes
INFO    | fasthttp    | WebSocket connections: 1
INFO    | fasthttp    | WebSocket connecting: wss://echo.websocket.org
INFO    | fasthttp    | ✔ WebSocket connected: wss://echo.websocket.org
Received: Hello from fasthttp!
INFO    | fasthttp    | WebSocket closed: wss://echo.websocket.org
INFO    | fasthttp    | Done in 0.53s
```

---

## `@app.ws()` Signature

```python
@app.ws(
    url: str,
    *,
    reconnect: bool = False,
    max_retries: int = 0,
    tags: list[str] | None = None,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `str` | — | WebSocket endpoint, must start with `ws://` or `wss://`. |
| `reconnect` | `bool` | `False` | Automatically reconnect when the connection drops. |
| `max_retries` | `int` | `0` | Max reconnect attempts (ignored when `reconnect=False`). `-1` = unlimited. |
| `tags` | `list[str]` | `None` | Tags for grouping and filtering routes. |

---

## Sending Messages

```python
await ws.send("Hello")              # text
await ws.send(b"\x00\xff")          # binary
await ws.send({"key": "value"})     # dict/list — auto-serialized to JSON
await ws.send_str("Hello")          # explicit text
await ws.send_bytes(b"\x00\xff")    # explicit binary
```

`send()` accepts `str`, `bytes`, `dict`, or `list`. Dictionaries and lists are automatically serialized to JSON via orjson.

---

## Receiving Messages

### Single message

```python
msg = await ws.recv()              # -> WebSocketMessage
msg = await ws.recv_str()          # -> str (raises TypeError on binary)
msg = await ws.recv_bytes()        # -> bytes (raises TypeError on text)
```

### `WebSocketMessage` object

```python
msg = await ws.recv()

msg.text        # str | None  — the message as text (None if binary)
msg.data        # str | bytes — the raw underlying data
msg.json()      # dict | list — parsed JSON body

str(msg)        # str representation
```

### Streaming with `async for`

```python
@app.ws(url="wss://stream.binance.com:9443/ws/btcusdt@trade")
async def trades(ws: WebSocket) -> None:
    async for msg in ws:
        trade = msg.json()
        print(f"BTC price: {trade['p']}")
```

The loop exits cleanly when the connection is closed.

---

## Connection Properties

```python
ws.closed           # bool — is the connection closed?
ws.local_address    # (host, port) — local endpoint
ws.remote_address   # (host, port) — remote server endpoint
```

---

## Connection Lifecycle

### Manual close

```python
await ws.close(code=1000, reason="done")
```

Standard WebSocket close codes:

| Code | Meaning |
|------|---------|
| `1000` | Normal closure |
| `1001` | Going away (server restart, client navigation) |
| `1008` | Policy violation |
| `1011` | Unexpected server error |

### Ping / Pong

```python
await ws.ping()           # send a ping
await ws.pong()           # send a pong
```

Heartbeat is handled automatically by the underlying `websockets` library.

---

## Auto-Reconnect

When `reconnect=True`, the client reconnects with exponential backoff (`2^attempt` seconds, capped at 30s) if the connection drops.

```python
@app.ws(url="wss://ws-feed.exchange.com", reconnect=True, max_retries=5)
async def market_data(ws: WebSocket) -> None:
    """Reconnect up to 5 times with backoff."""
    async for msg in ws:
        process(msg)
```

Set `max_retries=-1` for unlimited reconnection attempts.

---

## Running with HTTP Routes

WebSocket and HTTP routes run together. HTTP requests complete first, then the app stays alive until all WebSocket connections are closed or interrupted.

```python
from fasthttp import FastHTTP, WebSocket
from fasthttp.response import Response

app = FastHTTP()


@app.get(url="https://api.example.com/status")
async def health(resp: Response) -> dict:
    return resp.json()


@app.ws(url="wss://stream.example.com/feed")
async def feed(ws: WebSocket) -> None:
    async for msg in ws:
        print(msg)


if __name__ == "__main__":
    app.run()  # HTTP completes first, then WS stays alive until Ctrl+C
```

---

## Error Handling

```python
from fasthttp.websocket import WebSocketError, WebSocketConnectionError


async def safe_handler(ws: WebSocket) -> None:
    try:
        await ws.send("ping")
        msg = await ws.recv()
    except WebSocketConnectionError:
        print("Connection lost")
    except WebSocketError as e:
        print(f"WebSocket error: {e}")
```

---

## Dependencies

WebSocket support uses the [`websockets`](https://pypi.org/project/websockets/) library. It is included as a core dependency — no extra install step needed.

```bash
# Already works — websockets ships with fasthttp-client
pip install fasthttp-client
```

---

## Summary

| Feature | Available |
|---------|-----------|
| Text / binary / JSON messages | ✅ |
| `async for` iteration | ✅ |
| Auto-reconnect with backoff | ✅ |
| Ping / Pong | ✅ |
| Works with `app.run()` | ✅ |
| Works with HTTP routes | ✅ |
| Type-annotated handlers | ✅ |

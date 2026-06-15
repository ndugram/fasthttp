# WebSocket

FastHTTP поддерживает **WebSocket** для двусторонней связи в реальном времени.

WebSocket-роуты определяются через декоратор `@app.ws()` — тот же декларативный стиль, что и HTTP-роуты, но хэндлер получает объект `WebSocket` подключения вместо [`Response`](../../reference/response.md).

---

## Быстрый старт

Подключитесь к WebSocket echo-серверу, отправьте сообщение и получите ответ:

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

Запустите:

```bash
python main.py
```

Вывод:

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

## Сигнатура `@app.ws()`

```python
@app.ws(
    url: str,
    *,
    reconnect: bool = False,
    max_retries: int = 0,
    tags: list[str] | None = None,
)
```

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `url` | `str` | — | Адрес WebSocket, обязательно начинается с `ws://` или `wss://`. |
| `reconnect` | `bool` | `False` | Автоматически переподключаться при разрыве. |
| `max_retries` | `int` | `0` | Максимум попыток переподключения (игнорируется при `reconnect=False`). `-1` = безлимит. |
| `tags` | `list[str]` | `None` | Теги для группировки и фильтрации роутов. |

---

## Отправка сообщений

```python
await ws.send("Hello")              # текст
await ws.send(b"\x00\xff")          # бинарные данные
await ws.send({"key": "value"})     # dict/list — автосериализация в JSON
await ws.send_str("Hello")          # явная отправка текста
await ws.send_bytes(b"\x00\xff")    # явная отправка бинарных данных
```

`send()` принимает `str`, `bytes`, `dict` или `list`. Словари и списки автоматически сериализуются в JSON через orjson.

---

## Получение сообщений

### Одиночное сообщение

```python
msg = await ws.recv()              # -> WebSocketMessage
msg = await ws.recv_str()          # -> str (TypeError если бинарные)
msg = await ws.recv_bytes()        # -> bytes (TypeError если текст)
```

### Объект `WebSocketMessage`

```python
msg = await ws.recv()

msg.text        # str | None  — текст (None если бинарные)
msg.data        # str | bytes — сырые данные
msg.json()      # dict | list — JSON-парсинг тела

str(msg)        # строковое представление
```

### Стриминг через `async for`

```python
@app.ws(url="wss://stream.binance.com:9443/ws/btcusdt@trade")
async def trades(ws: WebSocket) -> None:
    async for msg in ws:
        trade = msg.json()
        print(f"Цена BTC: {trade['p']}")
```

Цикл завершается автоматически при закрытии соединения.

---

## Свойства подключения

```python
ws.closed           # bool — закрыто ли соединение?
ws.local_address    # (host, port) — локальный адрес
ws.remote_address   # (host, port) — адрес сервера
```

---

## Жизненный цикл

### Ручное закрытие

```python
await ws.close(code=1000, reason="готово")
```

Стандартные WebSocket коды закрытия:

| Код | Значение |
|-----|----------|
| `1000` | Нормальное завершение |
| `1001` | Уход (рестарт сервера, уход со страницы) |
| `1008` | Нарушение политики |
| `1011` | Непредвиденная ошибка сервера |

### Ping / Pong

```python
await ws.ping()           # отправить ping
await ws.pong()           # отправить pong
```

Heartbeat обрабатывается автоматически библиотекой `websockets`.

---

## Автопереподключение

При `reconnect=True` клиент переподключается с экспоненциальной задержкой (`2^attempt` секунд, не более 30с) в случае разрыва.

```python
@app.ws(url="wss://ws-feed.exchange.com", reconnect=True, max_retries=5)
async def market_data(ws: WebSocket) -> None:
    """Переподключаться до 5 раз с экспоненциальной задержкой."""
    async for msg in ws:
        process(msg)
```

Установите `max_retries=-1` для безлимитных попыток переподключения.

---

## Совместная работа с HTTP

WebSocket и HTTP роуты выполняются вместе. HTTP-запросы завершаются первыми, затем приложение остаётся висеть на WebSocket-соединениях до закрытия или Ctrl+C.

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
    app.run()  # HTTP выполняется первым, WS остаётся активным до Ctrl+C
```

---

## Обработка ошибок

```python
from fasthttp.websocket import WebSocketError, WebSocketConnectionError


async def safe_handler(ws: WebSocket) -> None:
    try:
        await ws.send("ping")
        msg = await ws.recv()
    except WebSocketConnectionError:
        print("Соединение потеряно")
    except WebSocketError as e:
        print(f"Ошибка WebSocket: {e}")
```

---

## Зависимости

WebSocket использует библиотеку [`websockets`](https://pypi.org/project/websockets/). Она уже включена в основные зависимости — ничего дополнительно устанавливать не нужно.

```bash
# Всё работает из коробки
pip install fasthttp-client
```

---

## Краткая сводка

| Возможность | Доступно |
|-------------|----------|
| Текстовые / бинарные / JSON сообщения | ✅ |
| `async for` итерация | ✅ |
| Автопереподключение с задержкой | ✅ |
| Ping / Pong | ✅ |
| Работает с `app.run()` | ✅ |
| Работает вместе с HTTP | ✅ |
| Валидация аннотаций типов | ✅ |

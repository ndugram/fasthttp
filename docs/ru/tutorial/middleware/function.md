# Function-based Middleware

`@app.middleware("http")` регистрирует обычную async-функцию как middleware — в стиле FastAPI, без наследования от `BaseMiddleware`.

```python
import time
from fasthttp import FastHTTP, Request
from fasthttp.response import Response

app = FastHTTP()


@app.middleware("http")
async def timing(request: Request, call_next):
    start = time.monotonic()
    response = await call_next(request)
    if response is not None:
        response.headers["X-Elapsed"] = str(time.monotonic() - start)
    return response


@app.get(url="https://httpbin.org/get")
async def get_data(resp: Response) -> dict:
    return resp.json()


app.run()
```

!!! note "Пока поддерживается только `"http"`"
    WebSocket (`@app.ws`) и GraphQL (`@app.graphql`) запросы не проходят
    через `HTTPClient`, поэтому через этот декоратор пока не идут.
    Вызов `app.middleware("ws")` или `app.middleware("graphql")`
    выбрасывает `ValueError`. Пока используйте
    [`BaseMiddleware`](creating.md) или
    [event hooks](../../middleware.md#event-hooks).

## Паттерн `call_next`

В отличие от `BaseMiddleware`, где `request()`/`response()` — два разных
метода, function-middleware оборачивает **весь** вызов одной корутиной —
включая retry, редиректы, class-based `BaseMiddleware` и сам обработчик
роута:

```
add_trace_id ─┐                                   ┌─ (всё после call_next)
              await call_next(request) ──▶ retries/redirects/BaseMiddleware/handler
              (всё до call_next) ◀──────────────────┘
```

Всё, что **до** `await call_next(request)`, выполняется до отправки
запроса. Всё, что **после**, — уже после того как пришёл ответ (или
`None` при ошибке), причём результат обработчика роута к этому моменту
уже обработан.

Зарегистрируй несколько — они вложатся как стек, **первая
зарегистрированная — самая внешняя**:

```python
@app.middleware("http")
async def outer(request: Request, call_next):
    print("outer: before")
    response = await call_next(request)
    print("outer: after")
    return response


@app.middleware("http")
async def inner(request: Request, call_next):
    print("inner: before")
    response = await call_next(request)
    print("inner: after")
    return response
```

Порядок: `outer: before` → `inner: before` → запрос отправлен → `inner: after` → `outer: after`.

## Короткое замыкание

Верни значение, не вызывая `call_next(request)`, чтобы полностью
пропустить запрос — полезно для auth-guard'ов или кэш-шорткатов:

```python
@app.middleware("http")
async def block_blank_host(request: Request, call_next):
    if not request.host:
        return None
    return await call_next(request)
```

## `Request`

`Request` описывает исходящий запрос *до* отправки. В отличие от
входящего ASGI-запроса, тело уже полностью собрано — стримить нечего,
поэтому мутабелен только `.headers`, и только он реально влияет на
отправляемый запрос. `.json` / `.content` / `.query_params` — это
read-only снимки для инспекции (логирование, трейсинг) — их изменение
ни на что не влияет, ровно как и `kwargs["json"]`/`kwargs["data"]` в
`BaseMiddleware.request()` уже сегодня.

| Атрибут | Тип | Описание |
|---------|-----|----------|
| `method` | `str` | HTTP-метод отправляемого запроса |
| `url` | `httpx.URL` | Структурированный URL — `.host`, `.port`, `.scheme`, `.path`, `.params` |
| `host` | `str \| None` | Шорткат для `request.url.host` |
| `headers` | `dict[str, str]` | **Мутабельно** — изменения уходят вместе с запросом |
| `query_params` | `dict[str, Any]` | Read-only снимок query-параметров, которые будут отправлены |
| `json` | `dict \| None` | Read-only снимок JSON-тела, если есть |
| `content` | `Any` | Read-only снимок сырого тела/form-data, если есть |
| `route` | `Route` | Выполняемый `Route` — `tags`, `response_model` и т.д. |
| `app` | `FastHTTP` | Экземпляр приложения — доступ к конфигу уровня app из middleware |
| `state` | `SimpleNamespace` | Scratch-пространство на один запрос — положи данные до `call_next`, прочитай после |

### `.state` для передачи данных между фазами

```python
@app.middleware("http")
async def timing(request: Request, call_next):
    request.state.start = time.monotonic()
    response = await call_next(request)
    elapsed = time.monotonic() - request.state.start
    if response is not None:
        response.headers["X-Elapsed"] = f"{elapsed:.3f}"
    return response
```

## Совмещение с class-based middleware

Function middleware (`@app.middleware("http")`) и `BaseMiddleware`
(`FastHTTP(middleware=[...])`) можно использовать вместе. Function
middleware всегда оборачивает **снаружи** — видит запрос первой и ответ
последней, а все `BaseMiddleware` и обработчик роута выполняются между
этими точками.

## Смотри также

- [Создание Middleware](creating.md) — API class-based `BaseMiddleware`
- [Middleware Reference](../../reference/middleware.md) — полный справочник API

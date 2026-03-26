# Защита SSRF

Защита от Server-Side Request Forgery.

## Что такое SSRF?

SSRF (Server-Side Request Forgery) - это атака, при которой злоумышленник заставляет сервер делать запросы к внутренним ресурсам.

## Как это работает

FastHTTP автоматически блокирует запросы к:

- `localhost` и варианты
- `127.0.0.1`, `0.0.0.0`, `::1`
- Приватные IP: `10.x.x.x`, `192.168.x.x`, `172.16-31.x.x`
- Link-local адреса: `169.254.x.x`
- Домены: `.local`, `.intranet`, `.internal`

## Пример

```python
from fasthttp import FastHTTP

app = FastHTTP()

# Этот запрос будет заблокирован автоматически
@app.get(url="http://localhost:8080/admin")
async def blocked_request(resp):
    return resp.json()


app.run()
# Результат: SSRF blocked
```

## Отключение

Можно отключить защиту SSRF:

```python
app = FastHTTP(security=False)
```

Не рекомендуется без особой необходимости.

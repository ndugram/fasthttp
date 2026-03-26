# Класс Response

Объект ответа.

## Атрибуты

| Атрибут | Тип | Описание |
|---------|-----|----------|
| `status` | `int` | Код статуса HTTP |
| `text` | `str` | Сырое тело ответа |
| `headers` | `dict` | Заголовки ответа |
| `content` | `bytes` | Сырые байты |
| `method` | `str` | HTTP метод |

## Методы

### json()

Преобразовать тело ответа в JSON:

```python
data = resp.json()  # Возвращает dict или list
```

### req_json()

Получить JSON, отправленный с запросом:

```python
sent = resp.req_json()  # Возвращает dict или None
```

## Пример

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)


@app.get(url="https://api.example.com/data")
async def handler(resp: Response) -> dict:
    return {"status": resp.status, "data": resp.json(), "headers": resp.headers}
```

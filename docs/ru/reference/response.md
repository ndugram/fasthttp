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
| `url` | `str` | URL запроса |

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

### assets()

Извлечь URL-адреса CSS и JavaScript ресурсов из HTML-ответа:

```python
result = resp.assets()
# Возвращает: {"css": [...], "js": [...]}
```

**Параметры:**

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `css` | `bool` | `True` | Включать ссылки CSS |
| `js` | `bool` | `True` | Включать ссылки JavaScript |

**Примеры:**

```python
# Получить все ресурсы (CSS + JS)
@app.get(url="https://example.com")
async def handler(resp: Response):
    return resp.assets()
# Возвращает: {"css": ["https://example.com/style.css"], "js": ["https://example.com/app.js"]}

# Только CSS
@app.get(url="https://example.com")
async def handler(resp: Response):
    return resp.assets(js=False)
# Возвращает: {"css": [...], "js": []}

# Только JS
@app.get(url="https://example.com")
async def handler(resp: Response):
    return resp.assets(css=False)
# Возвращает: {"css": [], "js": [...]}
```

Метод парсит `<link rel="stylesheet" href="...">` для CSS и `<script src="...">` для JavaScript. Все URL нормализуются через `urljoin`, поэтому относительные пути преобразуются в абсолютные на основе URL запроса.

## Пример

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)


@app.get(url="https://api.example.com/data")
async def handler(resp: Response) -> dict:
    return {"status": resp.status, "data": resp.json(), "headers": resp.headers}
```

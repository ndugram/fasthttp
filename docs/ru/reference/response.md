# Класс Response

Объект ответа.

## Атрибуты

| Атрибут | Тип | Описание |
|---------|-----|----------|
| `status` | `int` | Код статуса HTTP |
| `text` | `str` | Сырое тело ответа строкой |
| `headers` | `dict` | Заголовки ответа |
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

### bytes()

Возвращает тело ответа в виде байт. Использует реальные байты от сервера; при недоступности — кодирует `text` в UTF-8:

```python
raw = resp.bytes()  # Возвращает bytes
```

**Применение:** загрузка изображений, PDF, zip-файлов и любого бинарного контента.

```python
@app.get(url="https://httpbin.org/image/png")
async def handler(resp: Response) -> dict:
    raw = resp.bytes()
    return {"size": len(raw), "is_png": raw[:4] == b"\x89PNG"}
```

### html()

Возвращает тело ответа как HTML-строку. Бросает `ValueError`, если `Content-Type` не является HTML:

```python
html = resp.html()  # Возвращает str
```

**Бросает:** `ValueError` — если `Content-Type` присутствует и не содержит `html`.

```python
@app.get(url="https://example.com")
async def handler(resp: Response) -> dict:
    html = resp.html()
    return {"length": len(html)}
```

### xml()

Парсит тело ответа как XML и возвращает корневой `xml.etree.ElementTree.Element`:

```python
root = resp.xml()  # Возвращает ET.Element
```

**Бросает:** `xml.etree.ElementTree.ParseError` — если тело не является валидным XML.

```python
@app.get(url="https://feeds.bbci.co.uk/news/rss.xml")
async def handler(resp: Response) -> dict:
    root = resp.xml()
    channel = root.find("channel")
    return {"title": channel.findtext("title")}
```

!!! warning
    Использует стандартный XML-парсер — уязвим к XXE-атакам. Используйте только с доверенными источниками.

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

# Обработка ответа

Узнайте, как работать с HTTP ответами.

## Доступ к данным ответа

```python
@app.get(url="https://api.example.com/data")
async def handle_response(resp: Response) -> dict:
    # Код статуса (200, 404, 500 и т.д.)
    status = resp.status
    
    # JSON тело
    data = resp.json()
    
    # Текстовый ответ
    text = resp.text
    
    # Заголовки ответа
    headers = resp.headers
    
    # Сырые байты
    content = resp.content
    
    return {"status": status, "data": data}
```

## Методы ответа

### json()

Преобразует тело ответа в JSON:

```python
data = resp.json()  # Возвращает dict или list
```

### text

Возвращает сырой текст:

```python
text = resp.text  # Возвращает str
```

### req_json()

Возвращает JSON, который был отправлен с запросом:

```python
# Для POST запроса с json={"name": "John"}
sent = resp.req_json()  # Возвращает {"name": "John"}
```

### assets()

Извлекает URL-адреса CSS и JavaScript ресурсов из HTML-страницы:

```python
# Получить все ресурсы
result = resp.assets()
# Returns: {"css": [...], "js": [...]}

# Только CSS
css_only = resp.assets(js=False)

# Только JS
js_only = resp.assets(css=False)
```

Метод парсит:
- CSS: теги `<link rel="stylesheet" href="...">`
- JS: теги `<script src="...">`

Все ссылки нормализуются относительно URL запроса.

## Обработка ошибок

FastHTTP автоматически обрабатывает ошибки:

```python
@app.get(url="https://httpbin.org/status/404")
async def handle_error(resp: Response) -> dict:
    return {"status": resp.status}


@app.get(url="https://httpbin.org/status/500")
async def handle_server_error(resp: Response) -> dict:
    return {"status": resp.status}
```

### Проверка на ошибки

```python
@app.get(url="https://api.example.com/data")
async def check_response(resp: Response) -> dict | None:
    if resp is None:
        return {"error": "Request failed"}
    
    if resp.status >= 400:
        return {"error": f"HTTP {resp.status}"}
    
    return resp.json()
```

## Свойства ответа

| Свойство | Тип | Описание |
|----------|-----|----------|
| `status` | `int` | Код статуса HTTP |
| `text` | `str` | Сырое тело ответа |
| `headers` | `dict` | Заголовки ответа |
| `content` | `bytes` | Сырые байты |
| `method` | `str` | Используемый HTTP метод |

# Руководство по быстрому старту

Начните работу с FastHTTP Client менее чем за 2 минуты!

## Установка

```bash
pip install fasthttp-client
```

## Ваш первый запрос

Создайте файл `example.py`:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

# Создайте приложение
app = FastHTTP()

# Зарегистрируйте GET запрос
@app.get(url="https://httpbin.org/get")
async def get_data(resp: Response) -> str:
    return resp.json()  # Возвращает JSON данные

# Запустите все запросы
if __name__ == "__main__":
    app.run()
```

Запустите:
```bash
python example.py
```

**Вывод:**
```
16:09:18.955 │ INFO     │ fasthttp │ ✔ FastHTTP запущен
16:09:18.955 │ INFO     │ fasthttp │ ✔ Отправка 1 запроса
16:09:19.519 │ INFO     │ fasthttp │ ✔ ← GET https://httpbin.org/get [200] 458.26ms
16:09:19.520 │ INFO     │ fasthttp │ ✔ ✔️ GET     https://httpbin.org/get    200 458.26ms
16:09:19.520 │ DEBUG    │ fasthttp │ ↳ {"args": {}, "headers": {"Accept": "*/*", ...}, "url": "https://httpbin.org/get"}
16:09:20.037 │ INFO     │ fasthttp │ ✔ Завершено за 1.08s
```

## Базовая конфигурация

### Добавление пользовательских заголовков
```python
app = FastHTTP(
    get_request={
        "headers": {
            "User-Agent": "MyApp/1.0",
            "Authorization": "Bearer your-token",
        },
        "timeout": 10,
    },
)
```

### Включение режима отладки
```python
app = FastHTTP(debug=True)  # Показывает подробное логирование
```

## HTTP методы

### GET запрос
```python
@app.get(url="https://api.example.com/users")
async def get_users(resp: Response):
    return resp.json()
```

### POST запрос с JSON
```python
@app.post(url="https://api.example.com/users", json={"name": "John", "age": 30})
async def create_user(resp: Response):
    return f"Создан пользователь со статусом: {resp.status}"
```

### POST с данными формы
```python
@app.post(url="https://api.example.com/upload", data={"key": "value"})
async def upload_data(resp: Response):
    return resp.text
```

### PUT/PATCH запросы
```python
@app.put(url="https://api.example.com/users/1", json={"name": "Jane"})
async def update_user(resp: Response):
    return resp.json()

@app.patch(url="https://api.example.com/users/1", json={"age": 25})
async def patch_user(resp: Response):
    return resp.status
```

### DELETE запрос
```python
@app.delete(url="https://api.example.com/users/1")
async def delete_user(resp: Response):
    return f"Статус удаления: {resp.status}"
```

## Обработка ответов

### JSON ответ
```python
@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def get_post(resp: Response):
    data = resp.json()
    return f"Заголовок поста: {data['title']}"
```

### Текстовый ответ
```python
@app.get(url="https://httpbin.org/html")
async def get_html(resp: Response):
    return resp.text[:100]  # Первые 100 символов
```

### Код статуса
```python
@app.get(url="https://httpbin.org/status/404")
async def check_status(resp: Response):
    return f"Статус: {resp.status}, Заголовки: {dict(resp.headers)}"
```

## Автоматическая обработка ошибок

FastHTTP автоматически перехватывает и логирует все HTTP ошибки:

- **Ошибки соединения** - когда сервер недоступен
- **Ошибки таймаута** - когда запрос занимает слишком много времени
- **Ошибки HTTP статуса** - когда сервер возвращает коды 4xx/5xx

```python
from fasthttp import FastHTTP
from fasthttp.exceptions import FastHTTPConnectionError, FastHTTPTimeoutError, FastHTTPBadStatusError

app = FastHTTP(debug=True)

# Эти запросы будут автоматически логировать ошибки:
@app.get(url="https://несуществующий-домен.com/api")  # Ошибка соединения
@app.get(url="https://httpbin.org/delay/10")          # Ошибка таймаута  
@app.get(url="https://httpbin.org/status/404")        # Ошибка HTTP 404

if __name__ == "__main__":
    app.run()
```

**Пример вывода с ошибками:**
```
ERROR | fasthttp.exceptions | ✖ FastHTTPConnectionError: Соединение не удалось | URL: https://несуществующий-домен.com/api | Method: GET
ERROR | fasthttp.exceptions | ✖ FastHTTPTimeoutError: Превышено время ожидания | URL: https://httpbin.org/delay/10 | Details: timeout=10
ERROR | fasthttp.exceptions | ✖ FastHTTPBadStatusError: HTTP 404 | URL: https://httpbin.org/status/404 | Status: 404
```

Вы также можете вручную вызывать эти исключения в ваших обработчиках:
```python
@app.get(url="https://api.example.com/data")
async def get_data(resp: Response):
    if resp.status == 404:
        raise FastHTTPBadStatusError("Данные не найдены", url="https://api.example.com/data", status_code=404)
    return resp.json()
```

## Несколько запросов

> **Важно:** Если у вас 2 и более запроса, они выполняются параллельно.

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()

# Несколько GET запросов
@app.get(url="https://httpbin.org/get")
async def get_data(resp: Response):
    return resp.json()

@app.get(url="https://jsonplaceholder.typicode.com/users/1")
async def get_user(resp: Response):
    return resp.json()

# POST запрос
@app.post(url="https://httpbin.org/post", json={"test": "data"})
async def post_data(resp: Response):
    return resp.json()

if __name__ == "__main__":
    app.run()
```

## Продвинутые примеры

### Пример с GitHub API
```python
app = FastHTTP(
    get_request={
        "headers": {
            "Authorization": "Bearer YOUR_GITHUB_TOKEN",
            "User-Agent": "FastHTTP-App",
        },
    },
)

@app.get(url="https://api.github.com/user")
async def get_github_user(resp: Response):
    user_data = resp.json()
    return f"Привет, {user_data['name']}! У вас {user_data['public_repos']} публичных репозиториев."

@app.get(url="https://api.github.com/repos/microsoft/vscode")
async def get_vscode_stats(resp: Response):
    repo_data = resp.json()
    return f"VS Code имеет {repo_data['stargazers_count']} звезд!"
```

## Возвращаемые значения

Ваша функция-обработчик может возвращать:

- **str** - Будет залогировано как результат
- **int** - Код статуса (рекомендуется)
- **dict/list** - JSON данные (будут автоматически преобразованы в строку для логирования)
- **Response объект** - Полный объект ответа

```python
# Все это работает:
@app.get(url="https://example.com")
async def example1(resp: Response):
    return resp.status  # Возвращает 200

@app.get(url="https://example.com")
async def example2(resp: Response):
    return resp.json()  # Возвращает JSON данные

@app.get(url="https://example.com")
async def example3(resp: Response):
    return f"Статус: {resp.status}"  # Возвращает строку
```

## Следующие шаги

- Прочитайте [Справочник API](api-reference.md) для подробной документации
- Посмотрите [Примеры](examples.md) для большего количества случаев использования
- Изучите [Конфигурацию](configuration.md) для настроек

**Счастливого кодирования!**

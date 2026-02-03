# Примеры

Реальные примеры и случаи использования FastHTTP Client.

## 📚 Содержание

- [Интеграция с GitHub API](#интеграция-с-github-api)
- [Примеры JSONPlaceholder](#примеры-jsonplaceholder)
- [Тестирование HTTPBin](#тестирование-httpbin)
- [Загрузка файлов](#загрузка-файлов)
- [Примеры аутентификации](#примеры-аутентификации)
- [Обработка ошибок](#обработка-ошибок)
- [Тестирование производительности](#тестирование-производительности)

## 🐙 Интеграция с GitHub API

### Получение информации о пользователе
```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(
    get_request={
        "headers": {
            "Authorization": "Bearer YOUR_GITHUB_TOKEN",
            "User-Agent": "FastHTTP-GitHub-App",
        },
        "timeout": 10,
    },
)

@app.get(url="https://api.github.com/user")
async def get_current_user(resp: Response):
    user_data = resp.json()
    return f"""
👤 Пользователь: {user_data['name']} (@{user_data['login']})
📧 Email: {user_data['email']}
🏢 Компания: {user_data.get('company', 'Н/Д')}
📍 Местоположение: {user_data.get('location', 'Н/Д')}
📊 Публичных репозиториев: {user_data['public_repos']}
⭐ Подписчиков: {user_data['followers']}
👥 Подписок: {user_data['following']}
"""

@app.get(url="https://api.github.com/repos/microsoft/vscode")
async def get_vscode_stats(resp: Response):
    repo = resp.json()
    return f"""
📦 Репозиторий: {repo['full_name']}
⭐ Звезды: {repo['stargazers_count']}
🍴 Форки: {repo['forks_count']}
🐛 Открытых issues: {repo['open_issues_count']}
📝 Язык: {repo['language']}
📅 Обновлен: {repo['updated_at']}
"""

@app.get(url="https://api.github.com/users/octocat")
async def get_octocat_profile(resp: Response):
    user = resp.json()
    return f"🐙 Octocat: {user['name']} - {user['bio']}"

if __name__ == "__main__":
    app.run()
```

### Поиск репозиториев
```python
app = FastHTTP(
    get_request={
        "headers": {
            "Authorization": "Bearer YOUR_TOKEN",
            "Accept": "application/vnd.github.v3+json",
        },
    },
)

@app.get(url="https://api.github.com/search/repositories")
async def search_python_repos(resp: Response):
    data = resp.json()
    repos = data['items'][:5]  # Топ-5 результатов
    
    result = "🔍 Топ репозитории Python:\n\n"
    for i, repo in enumerate(repos, 1):
        result += f"{i}. {repo['full_name']} ⭐ {repo['stargazers_count']}\n"
        result += f"   📝 {repo['description'] or 'Без описания'}\n\n"
    
    return result

if __name__ == "__main__":
    app.run()
```

## 📝 Примеры JSONPlaceholder

### Управление постами блога
```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()

# Получить все посты
@app.get(url="https://jsonplaceholder.typicode.com/posts")
async def get_all_posts(resp: Response):
    posts = resp.json()
    return f"📚 Найдено {len(posts)} постов"

# Получить конкретный пост
@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def get_post(resp: Response):
    post = resp.json()
    return f"""
📖 Пост #{post['id']}: {post['title']}
👤 ID пользователя: {post['userId']}
📄 Текст: {post['body'][:100]}...
"""

# Создать новый пост
@app.post(url="https://jsonplaceholder.typicode.com/posts", json={
    "title": "FastHTTP Client",
    "body": "Это потрясающий HTTP клиент!",
    "userId": 1
})
async def create_post(resp: Response):
    new_post = resp.json()
    return f"✅ Создан пост #{new_post['id']}: {new_post['title']}"

# Обновить пост
@app.put(url="https://jsonplaceholder.typicode.com/posts/1", json={
    "id": 1,
    "title": "Обновлено с FastHTTP",
    "body": "Обновленный контент",
    "userId": 1
})
async def update_post(resp: Response):
    updated = resp.json()
    return f"🔄 Обновлен пост #{updated['id']}"

# Удалить пост
@app.delete(url="https://jsonplaceholder.typicode.com/posts/1")
async def delete_post(resp: Response):
    return f"🗑️ Статус удаления: {resp.status}"

if __name__ == "__main__":
    app.run()
```

## 🌐 Тестирование HTTPBin

### Тестирование запросов
```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(
    get_request={
        "headers": {
            "User-Agent": "FastHTTP-Tester/1.0",
            "X-Custom-Header": "test-value",
        },
    },
)

@app.get(url="https://httpbin.org/get")
async def test_get(resp: Response):
    data = resp.json()
    return f"""
🌐 Результаты GET теста:
📡 URL: {data['url']}
🖥️ Origin: {data['origin']}
📋 Заголовков получено: {len(data['headers'])} заголовков
"""

@app.post(url="https://httpbin.org/post", json={
    "name": "FastHTTP",
    "version": "1.0",
    "features": ["async", "logging", "simple"]
})
async def test_post_json(resp: Response):
    data = resp.json()
    return f"""
📤 POST JSON тест:
📝 Отправлено: {data['json']}
✅ Content-Type: {data['headers']['Content-Type']}
"""

@app.post(url="https://httpbin.org/post", data={
    "username": "testuser",
    "password": "secret123"
})
async def test_post_form(resp: Response):
    data = resp.json()
    return f"""
📋 POST форма тест:
🔑 Данные формы: {data['form']}
"""

@app.get(url="https://httpbin.org/status/418")
async def test_status_code(resp: Response):
    return f"☕ Статус {resp.status}: Я чайник!"

@app.get(url="https://httpbin.org/delay/2")
async def test_delay(resp: Response):
    return f"⏰ Получен отложенный ответ через 2 секунды"

if __name__ == "__main__":
    app.run()
```

## 📁 Симуляция загрузки файлов

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()

@app.post(url="https://httpbin.org/post", data={
    "file": "fake_file_content",
    "description": "Test file upload"
})
async def simulate_file_upload(resp: Response):
    data = resp.json()
    return f"""
📤 Симуляция загрузки файла:
📁 Файлы: {data.get('files', {})}
📝 Форма: {data.get('form', {})}
"""

if __name__ == "__main__":
    app.run()
```

## 🔐 Примеры аутентификации

### Аутентификация с Bearer токеном
```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(
    get_request={
        "headers": {
            "Authorization": "Bearer YOUR_JWT_TOKEN",
        },
    },
)

@app.get(url="https://api.example.com/profile")
async def get_protected_profile(resp: Response):
    if resp.status == 200:
        user = resp.json()
        return f"👤 Добро пожаловать, {user['name']}!"
    elif resp.status == 401:
        return "❌ Неавторизован - Неверный токен"
    else:
        return f"❓ Статус {resp.status}"

@app.get(url="https://api.example.com/admin/dashboard")
async def get_admin_data(resp: Response):
    if resp.status == 403:
        return "🚫 Доступ запрещен - Требуются права администратора"
    elif resp.status == 200:
        return "✅ Доступ администратора предоставлен"
    else:
        return f"❓ Статус {resp.status}"
```

### Аутентификация с API ключом
```python
app = FastHTTP(
    get_request={
        "headers": {
            "X-API-Key": "your-api-key-here",
        },
    },
)

@app.get(url="https://api.weather.com/v1/current")
async def get_weather(resp: Response):
    weather = resp.json()
    return f"""
🌤️ Данные о погоде:
📍 Местоположение: {weather['location']}
🌡️ Температура: {weather['temperature']}°C
💨 Состояние: {weather['condition']}
"""
```

## ⚠️ Обработка ошибок

### Надежная обработка ошибок
```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)

@app.get(url="https://httpbin.org/status/404")
async def handle_404(resp: Response):
    if resp.status == 404:
        return "🔍 Ресурс не найден"
    return f"Статус: {resp.status}"

@app.get(url="https://httpbin.org/status/500")
async def handle_500(resp: Response):
    if resp.status >= 500:
        return "🔥 Произошла ошибка сервера"
    return f"Статус: {resp.status}"

@app.get(url="https://httpbin.org/delay/10")
async def handle_timeout(resp: Response):
    if resp is None:
        return "⏰ Запрос истек по таймауту"
    return f"✅ Получен ответ: {resp.status}"

if __name__ == "__main__":
    try:
        app.run()
    except Exception as e:
        print(f"💥 Неожиданная ошибка: {e}")
```

## ⚡ Тестирование производительности

### Тестирование параллельных запросов
```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()

# Несколько эндпоинтов для тестирования производительности
endpoints = [
    "https://httpbin.org/get",
    "https://jsonplaceholder.typicode.com/posts/1", 
    "https://reqres.in/api/users/1",
]

for i, endpoint in enumerate(endpoints):
    @app.get(url=endpoint)
    async def test_endpoint(resp: Response, endpoint=endpoint):
        return f"✅ {endpoint}: {resp.status} ({len(resp.text)} символов)"

if __name__ == "__main__":
    print("🚀 Начинаем тест производительности...")
    app.run()
```

### Симуляция нагрузочного тестирования
```python
app = FastHTTP()

# Симуляция нескольких вызовов API
for i in range(5):
    @app.get(url=f"https://httpbin.org/get?id={i}")
    async def load_test(resp: Response, i=i):
        data = resp.json()
        return f"Запрос {i}: ✅ {data['args']}"

if __name__ == "__main__":
    app.run()
```

## 🔄 Примеры реальных API

### Клиент REST API
```python
from fasthttp import FastHTTP
from fasthttp.response import Response

class APIClient:
    def __init__(self, base_url: str, api_key: str):
        self.app = FastHTTP(
            get_request={
                "headers": {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
            },
        )
        self.base_url = base_url
    
    def get_users(self):
        @self.app.get(url=f"{self.base_url}/users")
        async def handler(resp: Response):
            return resp.json()
        return self.app
    
    def create_user(self, user_data: dict):
        @self.app.post(url=f"{self.base_url}/users", json=user_data)
        async def handler(resp: Response):
            return resp.json()
        return self.app
    
    def run(self):
        self.app.run()

# Использование
client = APIClient("https://api.example.com", "your-api-key")
client.get_users()
client.create_user({"name": "John", "email": "john@example.com"})
client.run()
```

### Клиент Weather API
```python
app = FastHTTP(
    get_request={
        "headers": {
            "X-RapidAPI-Key": "your-rapidapi-key",
        },
    },
)

@app.get(url="https://weather-api.p.rapidapi.com/current")
async def get_weather(resp: Response):
    if resp.status == 200:
        weather = resp.json()
        return f"""
🌤️ Текущая погода:
📍 Местоположение: {weather['location']['name']}
🌡️ Температура: {weather['current']['temp_c']}°C
💨 Ветер: {weather['current']['wind_kph']} км/ч
☁️ Состояние: {weather['current']['condition']['text']}
"""
    return f"❌ Ошибка Weather API: {resp.status}"

if __name__ == "__main__":
    app.run()
```

## 🎯 Лучшие практики

### 1. Конфигурация окружения
```python
import os
from fasthttp import FastHTTP

# Используйте переменные окружения для конфиденциальных данных
api_key = os.getenv("API_KEY", "default-key")
base_url = os.getenv("API_BASE_URL", "https://api.example.com")

app = FastHTTP(
    get_request={
        "headers": {
            "Authorization": f"Bearer {api_key}",
        },
    },
)
```

### 2. Валидация ответа
```python
@app.get(url="https://api.example.com/data")
async def validated_response(resp: Response):
    if resp.status != 200:
        return f"❌ Ошибка: {resp.status}"
    
    try:
        data = resp.json()
        if not isinstance(data, list):
            return "❌ Ожидался ответ типа list"
        return f"✅ Получено {len(data)} элементов"
    except Exception:
        return "❌ Некорректный JSON ответ"
```

### 3. Переиспользуемая конфигурация
```python
class BaseAPIClient:
    def __init__(self, base_url: str, headers: dict):
        self.app = FastHTTP(get_request={"headers": headers})
        self.base_url = base_url
    
    def add_endpoint(self, method: str, path: str, **kwargs):
        url = f"{self.base_url}{path}"
        
        if method.upper() == "GET":
            return self.app.get(url=url, **kwargs)
        elif method.upper() == "POST":
            return self.app.post(url=url, **kwargs)
        # ... другие методы

# Использование
client = BaseAPIClient("https://api.github.com", {
    "Authorization": "token YOUR_TOKEN",
    "User-Agent": "FastHTTP-App",
})

client.add_endpoint("GET", "/user")
client.add_endpoint("GET", "/repos", params={"sort": "updated"})
```

---

*Эти примеры демонстрируют гибкость и мощь FastHTTP Client! 🚀*

*Для более продвинутого использования, см. [Справочник API](api-reference.md)* 📚

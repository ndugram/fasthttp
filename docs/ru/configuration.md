# Руководство по конфигурации

Продвинутые опции конфигурации и настройки для FastHTTP Client.

## 📚 Содержание

- [Базовая конфигурация](#базовая-конфигурация)
- [Настройки для конкретных запросов](#настройки-для-конкретных-запросов)
- [Конфигурация логирования](#конфигурация-логирования)
- [Настройки таймаута и повторных попыток](#настройки-таймаута-и-повторных-попыток)
- [Заголовки и аутентификация](#заголовки-и-аутентификация)
- [Переменные окружения](#переменные-окружения)
- [Пользовательские паттерны конфигурации](#пользовательские-паттерны-конфигурации)

## 🔧 Базовая конфигурация

### Глобальная конфигурация
Настройте значения по умолчанию для всех HTTP методов:

```python
from fasthttp import FastHTTP

app = FastHTTP(
    debug=False,  # Включить подробное логирование
    get_request={
        "headers": {"User-Agent": "MyApp/1.0"},
        "timeout": 10,
    },
    post_request={
        "headers": {"Content-Type": "application/json"},
        "timeout": 30,
    },
)
```

### Конфигурация для конкретных методов
Каждый HTTP метод может иметь свою собственную конфигурацию по умолчанию:

```python
app = FastHTTP(
    # Глобальные значения по умолчанию
    debug=True,
    
    # Конфигурация по умолчанию для GET
    get_request={
        "headers": {
            "Accept": "application/json",
            "User-Agent": "FastHTTP-Client/1.0",
        },
        "timeout": 5,
        "allow_redirects": True,
    },
    
    # Конфигурация по умолчанию для POST
    post_request={
        "headers": {
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        "timeout": 30,
        "allow_redirects": False,
    },
    
    # Конфигурация по умолчанию для PUT
    put_request={
        "headers": {
            "Content-Type": "application/json",
        },
        "timeout": 30,
    },
    
    # Конфигурация по умолчанию для PATCH
    patch_request={
        "headers": {
            "Content-Type": "application/json",
        },
        "timeout": 30,
    },
    
    # Конфигурация по умолчанию для DELETE
    delete_request={
        "headers": {
            "Accept": "application/json",
        },
        "timeout": 10,
    },
)
```

## 📝 Настройки для конкретных запросов

### Переопределение глобальных настроек
Индивидуальные запросы могут переопределять глобальную конфигурацию:

```python
# Использует глобальную конфигурацию GET + дополнительные параметры
@app.get(url="https://api.example.com/data", params={"page": 1})
async def get_data(resp: Response):
    return resp.json()

# Переопределение таймаута для конкретного запроса
@app.get(url="https://slow-api.com/data", params={"timeout": 60})
async def get_slow_data(resp: Response):
    return resp.json()

# Пользовательские заголовки для конкретного запроса
@app.post(
    url="https://api.example.com/upload",
    json={"file": "data"},
    data={"custom": "header"},  # Это будет объединено с глобальными заголовками
)
async def upload_data(resp: Response):
    return resp.status
```

### Параметры запроса
Добавьте параметры запроса к любому запросу:

```python
@app.get(
    url="https://api.example.com/search",
    params={
        "q": "fasthttp",
        "sort": "relevance",
        "page": 2,
        "per_page": 50,
    }
)
async def search(resp: Response):
    return resp.json()
```

## 📊 Конфигурация логирования

### Режим отладки
Включите подробное логирование для разработки:

```python
# Базовый режим отладки
app = FastHTTP(debug=True)

# Режим отладки с пользовательской конфигурацией
app = FastHTTP(debug=True)

# Логирование будет показывать:
# - Заголовки запроса
# - Заголовки ответа
# - Тело ответа (сокращенное)
# - Результаты обработчика
# - Информацию о времени
```

### Уровни логирования и вывод

#### Уровень Info (по умолчанию)
```
16:09:18.955 │ INFO     │ fasthttp │ ✔ FastHTTP запущен
16:09:19.520 │ INFO     │ fasthttp │ ✔ ✔️ GET     https://api.example.com  200 458.26ms
```

#### Уровень Debug
```
16:09:18.954 │ DEBUG    │ fasthttp │ 🐛 Зарегистрирован маршрут: GET https://api.example.com
16:09:19.519 │ DEBUG    │ fasthttp │ 🐛 → GET https://api.example.com | headers={...}
16:09:19.520 │ DEBUG    │ fasthttp │ ↳ {"data": "response content"}
```

### Пользовательское логирование
Для продвинутых сценариев логирования вы можете перехватывать логи программно:

```python
import logging
from fasthttp import FastHTTP

# Перехват логов
log_capture = []

class LogCapture(logging.Handler):
    def emit(self, record):
        log_capture.append(self.format(record))

# Добавьте пользовательский обработчик
app = FastHTTP(debug=True)
logger = logging.getLogger("fasthttp")
logger.addHandler(LogCapture())

# Запустите запросы
app.run()

# Обработайте захваченные логи
for log_entry in log_capture:
    print(f"ЗАХВАЧЕНО: {log_entry}")
```

## ⏱️ Настройки таймаута и повторных попыток

### Таймаут запроса
Установите таймаут для отдельных запросов или глобально:

```python
# Глобальный таймаут
app = FastHTTP(get_request={"timeout": 30})

# Таймаут для конкретного запроса
@app.get(url="https://fast-api.com/data", timeout=5)
async def fast_request(resp: Response):
    return resp.status

@app.get(url="https://slow-api.com/data", timeout=120)
async def slow_request(resp: Response):
    return resp.status
```

### Опции конфигурации таймаута

```python
# Различные типы конфигурации таймаута
timeout_config = {
    "timeout": 30,  # Общий таймаут запроса в секундах
    
    # Специфичная для aiohttp конфигурация таймаута
    "timeout": aiohttp.ClientTimeout(
        total=30,      # Общий таймаут
        connect=10,     # Таймаут подключения
        sock_read=10,  # Таймаут чтения сокета
    )
}
```

## 🔐 Заголовки и аутентификация

### Общие паттерны аутентификации

#### Bearer токен
```python
app = FastHTTP(
    get_request={
        "headers": {
            "Authorization": "Bearer YOUR_JWT_TOKEN",
        },
    },
)
```

#### API ключ
```python
app = FastHTTP(
    get_request={
        "headers": {
            "X-API-Key": "your-api-key",
        },
    },
)
```

#### Базовая аутентификация
```python
import base64

# Кодируйте учетные данные
credentials = base64.b64encode(b"username:password").decode()

app = FastHTTP(
    get_request={
        "headers": {
            "Authorization": f"Basic {credentials}",
        },
    },
)
```

#### Пользовательские паттерны заголовков
```python
app = FastHTTP(
    get_request={
        "headers": {
            # User agent
            "User-Agent": "FastHTTP-Client/1.0",
            
            # Типы содержимого
            "Content-Type": "application/json",
            "Accept": "application/json",
            
            # Пользовательские заголовки
            "X-Client-Version": "1.0.0",
            "X-Request-ID": "req-12345",
            
            # Управление кешем
            "Cache-Control": "no-cache",
            
            # CORS
            "Origin": "https://yourapp.com",
        },
    },
)
```

### Динамические заголовки
Для заголовков, которые изменяются для каждого запроса:

```python
import uuid
from datetime import datetime

def generate_headers():
    return {
        "X-Request-ID": str(uuid.uuid4()),
        "X-Timestamp": datetime.utcnow().isoformat(),
        "User-Agent": f"FastHTTP-Client/1.0-{uuid.uuid4().hex[:8]}",
    }

@app.get(url="https://api.example.com/data")
async def dynamic_headers_request(resp: Response):
    # Заголовки будут объединены с глобальной конфигурацией
    return resp.status
```

## 🌐 Переменные окружения

### Конфигурация с переменными окружения
Используйте переменные окружения для конфиденциальной и зависящей от окружения конфигурации:

```python
import os
from fasthttp import FastHTTP

# Читаем из окружения
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.example.com")
API_KEY = os.getenv("API_KEY")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
TIMEOUT = int(os.getenv("TIMEOUT", "30"))

# Настраиваем приложение с переменными окружения
app = FastHTTP(
    debug=DEBUG,
    get_request={
        "headers": {
            "Authorization": f"Bearer {API_KEY}",
            "User-Agent": os.getenv("USER_AGENT", "FastHTTP-Client/1.0"),
        },
        "timeout": TIMEOUT,
    },
)
```

### Конфигурация для разных окружений
Различные настройки для разных окружений:

```python
import os

ENV = os.getenv("ENVIRONMENT", "development")

if ENV == "production":
    app = FastHTTP(
        debug=False,
        get_request={
            "headers": {
                "User-Agent": "Production-App/1.0",
            },
            "timeout": 30,
        },
    )
elif ENV == "staging":
    app = FastHTTP(
        debug=True,
        get_request={
            "headers": {
                "User-Agent": "Staging-App/1.0",
            },
            "timeout": 60,
        },
    )
else:  # development
    app = FastHTTP(
        debug=True,
        get_request={
            "headers": {
                "User-Agent": "Dev-App/1.0",
            },
            "timeout": 10,
        },
    )
```

## 🎛️ Пользовательские паттерны конфигурации

### Классы конфигурации
Организуйте конфигурацию в классы:

```python
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class APIConfig:
    base_url: str
    api_key: str
    timeout: int = 30
    debug: bool = False
    headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {}
    
    def get_fasthttp_config(self, method: str) -> Dict[str, Any]:
        base_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "FastHTTP-Client/1.0",
        }
        base_headers.update(self.headers)
        
        return {
            "debug": self.debug,
            f"{method.lower()}_request": {
                "headers": base_headers,
                "timeout": self.timeout,
            },
        }

# Использование
github_config = APIConfig(
    base_url="https://api.github.com",
    api_key=os.getenv("GITHUB_TOKEN"),
    timeout=10,
    debug=True,
    headers={
        "Accept": "application/vnd.github.v3+json",
    },
)

app = FastHTTP(**github_config.get_fasthttp_config("GET"))
```

### Фабрика конфигурации
Создавайте фабрики конфигурации для разных API:

```python
class APIConfigFactory:
    @staticmethod
    def github(token: str, debug: bool = False):
        return FastHTTP(
            debug=debug,
            get_request={
                "headers": {
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "FastHTTP-GitHub/1.0",
                },
                "timeout": 10,
            },
        )
    
    @staticmethod
    def weather(api_key: str, debug: bool = False):
        return FastHTTP(
            debug=debug,
            get_request={
                "headers": {
                    "X-RapidAPI-Key": api_key,
                    "X-RapidAPI-Host": "weather-api.p.rapidapi.com",
                },
                "timeout": 15,
            },
        )
    
    @staticmethod
    def jsonplaceholder(debug: bool = False):
        return FastHTTP(
            debug=debug,
            get_request={
                "headers": {
                    "User-Agent": "FastHTTP-JSONPlaceholder/1.0",
                },
                "timeout": 10,
            },
        )

# Использование
github_client = APIConfigFactory.github(os.getenv("GITHUB_TOKEN"), debug=True)
weather_client = APIConfigFactory.weather(os.getenv("WEATHER_API_KEY"))
json_client = APIConfigFactory.jsonplaceholder()
```

### Валидация конфигурации
Валидируйте конфигурацию перед использованием:

```python
from typing import Optional
import os

class ValidatedConfig:
    def __init__(self):
        self.api_key = self._validate_api_key()
        self.base_url = self._validate_base_url()
        self.timeout = self._validate_timeout()
        self.debug = self._validate_debug()
    
    def _validate_api_key(self) -> str:
        key = os.getenv("API_KEY")
        if not key:
            raise ValueError("Переменная окружения API_KEY обязательна")
        return key
    
    def _validate_base_url(self) -> str:
        url = os.getenv("API_BASE_URL")
        if not url:
            raise ValueError("Переменная окружения API_BASE_URL обязательна")
        if not url.startswith(("http://", "https://")):
            raise ValueError("API_BASE_URL должен начинаться с http:// или https://")
        return url
    
    def _validate_timeout(self) -> int:
        timeout = os.getenv("TIMEOUT", "30")
        try:
            timeout_int = int(timeout)
            if timeout_int <= 0:
                raise ValueError("TIMEOUT должен быть положительным")
            return timeout_int
        except ValueError:
            raise ValueError("TIMEOUT должен быть корректным целым числом")
    
    def _validate_debug(self) -> bool:
        debug = os.getenv("DEBUG", "false")
        return debug.lower() in ("true", "1", "yes")

# Использование
try:
    config = ValidatedConfig()
    app = FastHTTP(
        debug=config.debug,
        get_request={
            "headers": {"Authorization": f"Bearer {config.api_key}"},
            "timeout": config.timeout,
        },
    )
except ValueError as e:
    print(f"Ошибка конфигурации: {e}")
    exit(1)
```

## 🔧 Продвинутые примеры конфигурации

### Мульти-окружение настройка
```python
import os
from enum import Enum

class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging" 
    PRODUCTION = "production"

def create_app_for_environment(env: Environment) -> FastHTTP:
    configs = {
        Environment.DEVELOPMENT: {
            "debug": True,
            "timeout": 30,
            "headers": {"User-Agent": "Dev-Client/1.0"},
        },
        Environment.STAGING: {
            "debug": True,
            "timeout": 60,
            "headers": {"User-Agent": "Staging-Client/1.0"},
        },
        Environment.PRODUCTION: {
            "debug": False,
            "timeout": 10,
            "headers": {"User-Agent": "Prod-Client/1.0"},
        },
    }
    
    config = configs[env]
    return FastHTTP(
        debug=config["debug"],
        get_request={
            "headers": config["headers"],
            "timeout": config["timeout"],
        },
    )

# Использование
env = Environment(os.getenv("ENVIRONMENT", "development"))
app = create_app_for_environment(env)
```

### Конфигурация в стиле плагинов
```python
class HTTPClientPlugin:
    def __init__(self, name: str):
        self.name = name
        self.headers = {}
        self.timeout = 30
    
    def add_header(self, key: str, value: str):
        self.headers[key] = value
    
    def set_timeout(self, timeout: int):
        self.timeout = timeout
    
    def configure_app(self, app: FastHTTP):
        method = self.name.upper()
        config = {
            "headers": self.headers.copy(),
            "timeout": self.timeout,
        }
        
        setattr(app, f"{method.lower()}_request", config)

# Использование
auth_plugin = HTTPClientPlugin("get")
auth_plugin.add_header("Authorization", "Bearer token")
auth_plugin.set_timeout(15)

app = FastHTTP()
auth_plugin.configure_app(app)
```

---

*Правильная конфигурация - ключ к созданию надежных HTTP клиентов! 🚀*

*Больше информации см. в [Справочнике API](api-reference.md) и [Примерах](examples.md)* 📚

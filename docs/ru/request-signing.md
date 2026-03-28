# Подпись запросов

FastHTTP включает встроенную автоматическую подпись запросов с использованием HMAC-SHA256. Эта функция добавляет криптографические подписи ко всем исходящим HTTP-запросам для проверки их подлинности и обнаружения изменений.

## Обзор

При включении каждый запрос автоматически подписывается с использованием:
- HTTP-метода
- Полного URL
- Временной метки (UNIX)
- Тела запроса (если есть)

Подпись добавляется в заголовки запроса:
- `X-Signature` - HMAC-SHA256 шестнадцатеричный дайджест
- `X-Timestamp` - Unix временная метка
- `X-Nonce` - Уникальное случайное значение для каждого запроса

## Как это работает

### Формат payload

```
METHOD + "\n" + URL + "\n" + TIMESTAMP + "\n" + BODY
```

Пример:
```
POST
https://api.example.com/users
1774629340
{"name":"John","email":"john@example.com"}
```

### Генерация подписи

1. Сериализация тела (dict/list → JSON, str → bytes, None → b"")
2. Создание строки payload
3. Вычисление HMAC-SHA256 с секретным ключом
4. Добавление заголовков к запросу

## Использование

### Базовое использование

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()

@app.get(url="https://api.example.com/data")
async def handler(resp: Response) -> dict:
    return resp.json()
```

Каждый запрос автоматически включает:
```
X-Signature: a9a5680104a42814fd6eeec345a7507d41fdcbc71cc636dd2a4dbd3a0566cf79
X-Timestamp: 1774629340
X-Nonce: 2bb9ca6b74f74f051859e39949ac9833
```

### Пользовательский секретный ключ

```python
import secrets
from fasthttp import FastHTTP

secret_key = secrets.token_bytes(32)
app = FastHTTP(secret_key=secret_key)
```

Если ключ не передан, он генерируется автоматически.

### Отключение подписи

```python
app = FastHTTP()
app.security.enable_signing(False)
```

## Функции безопасности

### Защита от атак повтора

- Проверка временной метки (макс. возраст: 300 секунд)
- Уникальный nonce на каждый запрос (16 байт случайных)

### Сравнение за постоянное время

Использует `hmac.compare_digest()` для проверки подписи для предотвращения атак по времени.

### Сериализация тела

- `dict`/`list` → JSON через orjson (с отсортированными ключами)
- `str` → UTF-8 байты
- `bytes` → как есть
- `None` → пустые байты

## Проверка на стороне сервера

Для проверки входящих подписанных запросов:

```python
import hmac
import time

def verify_signature(
    method: str,
    url: str,
    timestamp: int,
    body: bytes,
    signature: str,
    secret_key: bytes,
    max_age: int = 300
) -> bool:
    if abs(time.time() - timestamp) > max_age:
        return False
    
    payload = f"{method}\n{url}\n{timestamp}\n".encode() + body
    expected = hmac.new(secret_key, payload, digestmod="sha256").hexdigest()
    return hmac.compare_digest(expected, signature)
```

## Конфигурация

### Доступ к секретному ключу

```python
app = FastHTTP()
key = app.security.secret_key
```

### Включение/Отключение

```python
app.security.enable_signing(True)   # Включить
app.security.enable_signing(False)  # Отключить
```

## Справочник заголовков

| Заголовок | Тип | Описание |
|-----------|-----|----------|
| `X-Signature` | string | HMAC-SHA256 шестнадцатеричный дайджест |
| `X-Timestamp` | int | Unix временная метка |
| `X-Nonce` | string | 16-байтный случайный hex |

## Пример запроса

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)

@app.post(
    url="https://api.example.com/users",
    json={"name": "John", "email": "john@example.com"}
)
async def create_user(resp: Response) -> dict:
    return resp.json()

app.run()
```

Отладочный вывод показывает подписанные заголовки:
```
DEBUG | → POST https://api.example.com/users | headers={
    'User-Agent': 'fasthttp/1.0.0',
    'X-Signature': 'e9aebfc284a7f346...',
    'X-Timestamp': '1774629539',
    'X-Nonce': 'da4ec450399cf131...'
}
```

## Смотрите также

- [Безопасность](security.md) - Другие функции безопасности
- [Конфигурация](configuration.md) - Настройки приложения

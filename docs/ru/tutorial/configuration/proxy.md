# Прокси

Настройка прокси-сервера для запросов.

## Базовое использование

```python
from fasthttp import FastHTTP

app = FastHTTP(proxy="http://proxy.example.com:8080")
```

## Типы прокси

```python
# HTTP прокси
app = FastHTTP(proxy="http://proxy.example.com:8080")

# HTTPS прокси
app = FastHTTP(proxy="https://proxy.example.com:8080")

# Прокси с авторизацией
app = FastHTTP(proxy="http://user:password@proxy.example.com:8080")

# SOCKS5 прокси
app = FastHTTP(proxy="socks5://proxy.example.com:1080")
```

## Переменные окружения

```python
import os
from fasthttp import FastHTTP

app = FastHTTP(
    proxy=os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY"),
)
```

## Файл .env

```bash
HTTP_PROXY=http://proxy.example.com:8080
HTTPS_PROXY=http://proxy.example.com:8080
```

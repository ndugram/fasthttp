# HTTP/2 Support

FastHTTP поддерживает HTTP/2 для улучшенной производительности.

## Установка

Для HTTP/2 поддержки установите дополнительные зависимости:

```bash
pip install fasthttp-client[http2]
```

Это установит `httpx[http2]` в качестве зависимости.

## Включение HTTP/2

```python
from fasthttp import FastHTTP

app = FastHTTP(http2=True)
```

## Что такое HTTP/2?

HTTP/2 — это вторая версия протокола HTTP, которая обеспечивает:

- **Мультиплексирование** — несколько запросов через одно соединение
- **Сжатие заголовков** — меньше данных передаётся
- **Server Push** — сервер может отправлять данные заранее
- **Приоритизация** — более важные ресурсы загружаются первыми
- **Одно соединение** — не нужно создавать новое соединение для каждого запроса

## Преимущества HTTP/2

### До HTTP/2

```
Соединение 1: GET /page
Соединение 2: GET /style.css
Соединение 3: GET /script.js
Соединение 4: GET /image.png
```

### С HTTP/2

```
Соединение 1: GET /page, /style.css, /script.js, /image.png (параллельно)
```

## Пример использования

```python
from fasthttp import FastHTTP

app = FastHTTP(http2=True)


@app.get(url="https://httpbin.org/get")
async def get_data(resp):
    return resp.json()


@app.post(url="https://httpbin.org/post", json={"test": "data"})
async def post_data(resp):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

## Ограничения

- Не все серверы поддерживают HTTP/2
- Требует HTTPS (большинство браузеров)
- Не поддерживается в некоторых прокси

## Проверка HTTP/2

```python
from fasthttp import FastHTTP

app = FastHTTP(http2=True)


@app.get(url="https://httpbin.org/get")
async def check_http2(resp):
    # Проверяем, используется ли HTTP/2
    # (зависит от сервера)
    return {
        "status": resp.status,
        "http_version": resp.headers.get("server"),
    }
```

## Когда использовать HTTP/2

### Да

- Много параллельных запросов к одному хосту
- Высокая нагрузка на сеть
- Критична производительность

### Нет

- Простые одиночные запросы
- Сервер не поддерживает HTTP/2
- Нужна совместимость со старыми системами

## Смотрите также

- [Конфигурация](configuration.md) — настройки
- [Быстрый старт](quick-start.md) — основы

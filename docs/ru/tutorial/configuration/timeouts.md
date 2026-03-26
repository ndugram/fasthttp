# Таймауты

Настройка таймаутов запросов.

## Глобальный таймаут

```python
app = FastHTTP(get_request={"timeout": 30.0})
```

## Таймаут для запроса

```python
@app.get(url="https://api.example.com/fast", timeout=5.0)
async def fast_request(resp):
    return resp.json()


@app.get(url="https://api.example.com/slow", timeout=120.0)
async def slow_request(resp):
    return resp.json()
```

## Рекомендации

| Тип запроса | Таймаут |
|-------------|---------|
| GET запросы | 10-30 секунд |
| POST/PUT запросы | 30-60 секунд |
| Загрузка файлов | 120+ секунд |
| Быстрые проверки | 5-10 секунд |

## Встроенные таймауты

FastHTTP имеет встроенные таймауты:

- Таймаут соединения: 10 секунд
- Таймаут запроса: 30 секунд (по умолчанию)

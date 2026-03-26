# Логирование

Настройка логирования и режима отладки.

## Режим отладки

```python
# Подробный вывод
app = FastHTTP(debug=True)

# Минимальный вывод
app = FastHTTP(debug=False)
```

## Вывод отладки

При `debug=True`:

```
DEBUG   | fasthttp    | GET https://api.example.com/data | headers={'User-Agent': 'fasthttp/0.1.0'}
DEBUG   | fasthttp    | 200 | headers={'Content-Type': 'application/json'}
INFO    | fasthttp    | GET https://api.example.com/data 200 150.23ms
```

При `debug=False`:

```
INFO    | fasthttp    | GET https://api.example.com/data 200 150.23ms
```

## Что показывает отладка

### debug=True
- Заголовки запроса и ответа
- Тело запроса и ответа
- Время выполнения каждого запроса
- Полный URL с параметрами

### debug=False
- Только код статуса
- Время выполнения

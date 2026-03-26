# Первые шаги

Начните работу с FastHTTP менее чем за 2 минуты.

## Установка

Установите FastHTTP с помощью pip:

```bash
pip install fasthttp-client
```

Для поддержки HTTP/2:

```bash
pip install fasthttp-client[http2]
```

## Ваш первый запрос

Создайте файл `example.py`:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def main(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()
```

Запустите:

```bash
python example.py
```

Вывод:

```
INFO    | fasthttp    | FastHTTP started
INFO    | fasthttp    | Sending 1 requests
INFO    | fasthttp    | GET https://jsonplaceholder.typicode.com/posts/1 200 234.56ms
INFO    | fasthttp    | Done in 0.24s
```

## Важное требование

Функции-обработчики должны иметь аннотацию возвращаемого типа:

```python
async def handler(resp: Response) -> dict:  # Обязательно!
    return resp.json()
```

Без аннотации `-> dict` функция не будет работать.

## Как это работает

При вызове `app.run()`, FastHTTP:

1. Собирает все зарегистрированные маршруты
2. Проверяет наличие аннотаций типов
3. Создает асинхронные задачи для всех запросов
4. Выполняет запросы параллельно с помощью asyncio
5. Для каждого запроса:
   - Применяет зависимости
   - Запускает middleware.before_request()
   - Проверяет безопасность
   - Отправляет HTTP запрос через httpx
   - Запускает middleware.after_response()
   - Вызывает ваш обработчик с объектом Response
6. Логирует результаты

## Основные понятия

- **Маршрут**: Функция с декоратором `@app.get()`, `@app.post()` и т.д.
- **Обработчик**: Функция, которая обрабатывает ответ
- **Response**: Объект с ответом сервера (статус, тело, заголовки)
- **Зависимость**: Функция, модифицирующая конфиг запроса
- **Middleware**: Плагин для глобальной логики

## Следующие шаги

Продолжайте изучение:

- [HTTP методы](http-methods.md) - Все поддерживаемые методы
- [Параметры запроса](request-parameters.md) - Query, JSON, заголовки
- [Конфигурация](../en/configuration.md) - Дополнительные настройки

# Командная строка (CLI)

FastHTTP поставляется с удобным CLI для запуска запросов из терминала.

## Установка

CLI устанавливается вместе с пакетом:

```bash
pip install fasthttp-client
```

## Основное использование

```bash
fasthttp get https://jsonplaceholder.typicode.com/posts/1
```

## HTTP методы

### GET

```bash
fasthttp get https://api.example.com/data
```

С query параметрами в URL:

```bash
fasthttp get "https://api.example.com/search?q=test&page=1"
```

### POST

```bash
fasthttp post https://api.example.com/users --json '{"name": "John"}'
```

### PUT

```bash
fasthttp put https://api.example.com/users/1 --json '{"name": "Jane"}'
```

### PATCH

```bash
fasthttp patch https://api.example.com/users/1 --json '{"age": 25}'
```

### DELETE

```bash
fasthttp delete https://api.example.com/users/1
```

## Опции

### Заголовки (-H, --header)

```bash
fasthttp get https://api.example.com/data \
  -H "Authorization: Bearer token" \
  -H "User-Agent: MyApp/1.0"
```

Несколько заголовков через запятую:

```bash
fasthttp get https://api.example.com/data -H "Authorization: Bearer token,Content-Type: application/json"
```

### JSON тело (-j, --json)

```bash
fasthttp post https://api.example.com/users \
  --json '{"name": "John", "email": "john@example.com"}'
```

### Form данные (-d, --data)

```bash
fasthttp post https://api.example.com/login \
  --data "username=john&password=secret"
```

### Таймаут (-t, --timeout)

```bash
fasthttp get https://api.example.com/data --timeout 60
```

По умолчанию 30 секунд.

### Режим отладки (--debug)

```bash
fasthttp get https://api.example.com/data --debug
```

Показывает:
- Заголовки запроса
- JSON/data тело
- Заголовки ответа

## Формат вывода

Второй аргумент после URL определяет что вывести:

### status — только статус (по умолчанию)

```bash
fasthttp get https://api.example.com/data status
# 200
```

### json — JSON тело ответа

```bash
fasthttp get https://api.example.com/data json
# {"id": 1, "name": "John"}
```

### text — текст ответа

```bash
fasthttp get https://api.example.com/data text
# <html>...</html>
```

### headers — заголовки ответа

```bash
fasthttp get https://api.example.com/data headers
# {"Content-Type": "application/json", "Date": "..."}
```

### all — всё вместе

```bash
fasthttp get https://api.example.com/data all
# Status: 200
# Elapsed: 234.56ms
# Headers: {...}
# Body: {...}
```

## Примеры

### Простой GET

```bash
$ fasthttp get https://jsonplaceholder.typicode.com/posts/1 json
{
  "userId": 1,
  "id": 1,
  "title": "sunt aut facere repellat provident occaecati",
  "body": "..."
}
```

### POST с JSON

```bash
$ fasthttp post https://jsonplaceholder.typicode.com/posts \
  --json '{"title": "foo", "body": "bar", "userId": 1}' json
{
  "title": "foo",
  "body": "bar",
  "userId": 1,
  "id": 101
}
```

### С заголовками

```bash
$ fasthttp get https://httpbin.org/headers \
  -H "Authorization: Bearer test-token" json
{
  "headers": {
    "Authorization": "Bearer test-token",
    "Host": "httpbin.org"
  }
}
```

### С отладкой

```bash
$ fasthttp get https://httpbin.org/get --debug
ℹ → GET https://httpbin.org/get
✔ HTTP 200 in 234.56ms
ℹ ← Response headers:
ℹ   Content-Type: application/json
ℹ   Date: Mon, 15 Jan 2025 10:30:00 GMT
```

### Проверить статус API

```bash
$ fasthttp get https://api.example.com/health
✔ HTTP 200 in 45.23ms
200
```

## Справка

```bash
fasthttp --help
fasthttp get --help
fasthttp post --help
```

## Смотрите также

- [Быстрый старт](quick-start.md) — основы
- [Конфигурация](configuration.md) — настройки
- [Примеры](examples.md) — больше примеров

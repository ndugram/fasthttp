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

С параметрами:

```bash
fasthttp get "https://api.example.com/search?q=test&page=1"
```

### POST

```bash
fasthttp post https://api.example.com/users json='{"name": "John"}'
```

### PUT

```bash
fasthttp put https://api.example.com/users/1 json='{"name": "Jane"}'
```

### PATCH

```bash
fasthttp patch https://api.example.com/users/1 json='{"age": 25}'
```

### DELETE

```bash
fasthttp delete https://api.example.com/users/1
```

## Параметры

### Заголовки

```bash
fasthttp get https://api.example.com/data \
  --header "Authorization: Bearer token" \
  --header "User-Agent: MyApp/1.0"
```

Сокращённая форма:

```bash
fasthttp get https://api.example.com/data -H "Authorization: Bearer token"
```

### Query параметры

```bash
fasthttp get https://api.example.com/search \
  --param "q=fast" \
  --param "page=1"
```

Сокращённая форма:

```bash
fasthttp get https://api.example.com/search -p "q=fast" -p "page=1"
```

### Таймаут

```bash
fasthttp get https://api.example.com/data --timeout 30
```

### JSON тело

```bash
fasthttp post https://api.example.com/users \
  --json '{"name": "John", "email": "john@example.com"}'
```

## Опции

### Режим отладки

```bash
fasthttp get https://api.example.com/data --debug
```

### Вывод в файл

```bash
fasthttp get https://api.example.com/data --output response.json
```

### Формат вывода

```bash
# JSON (по умолчанию)
fasthttp get https://api.example.com/data --format json

# Только статус
fasthttp get https://api.example.com/data --format status

# Только тело
fasthttp get https://api.example.com/data --format body
```

## Примеры

### Простой GET

```bash
$ fasthttp get https://jsonplaceholder.typicode.com/posts/1
{
  "userId": 1,
  "id": 1,
  "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
  "body": "..."
}
```

### POST с JSON

```bash
$ fasthttp post https://jsonplaceholder.typicode.com/posts \
  --json '{"title": "foo", "body": "bar", "userId": 1}'
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
  -H "Authorization: Bearer test-token" \
  -H "X-Custom-Header: value"
{
  "headers": {
    "Authorization": "Bearer test-token",
    "X-Custom-Header": "value",
    "Host": "httpbin.org"
  }
}
```

### С параметрами

```bash
$ fasthttp get "https://jsonplaceholder.typicode.com/posts" \
  -p "userId=1" -p "_limit=3"
[
  {
    "userId": 1,
    "id": 1,
    "title": "...",
    "body": "..."
  },
  ...
]
```

## Справка

```bash
fasthttp --help
```

Вывод:

```
usage: fasthttp [-h] [--debug] [--timeout TIMEOUT] [-H HEADER] [-p PARAM]
                [--json JSON] [--output OUTPUT] [--format FORMAT]
                method url

positional arguments:
  method                HTTP метод (get, post, put, patch, delete)
  url                   URL запроса

optional arguments:
  -h, --help            Показать справку
  --debug               Режим отладки
  --timeout TIMEOUT     Таймаут в секундах
  -H, --header HEADER   Заголовок (может быть несколько)
  -p, --param PARAM     Query параметр (может быть несколько)
  --json JSON           JSON тело запроса
  --output OUTPUT       Сохранить ответ в файл
  --format FORMAT       Формат вывода (json, status, body)
```

## Смотрите также

- [Быстрый старт](quick-start.md) — основы
- [Конфигурация](configuration.md) — настройки
- [Примеры](examples.md) — больше примеров

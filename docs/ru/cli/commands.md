# Команды CLI

Доступные команды CLI.

## HTTP методы

### GET

```bash
fasthttp get https://api.example.com/data
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

## Формат вывода

Второй аргумент определяет вывод:

| Формат | Описание |
|--------|----------|
| `status` | Только код статуса (по умолчанию) |
| `json` | JSON тело ответа |
| `text` | Текст ответа |
| `headers` | Заголовки ответа |
| `all` | Всё вместе |

## Примеры

```bash
# Только статус
$ fasthttp get https://api.example.com/data status
200

# JSON ответ
$ fasthttp get https://api.example.com/data json
{"id": 1, "name": "John"}
```

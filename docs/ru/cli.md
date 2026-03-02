# CLI

Командная строка для HTTP-запросов.

## Установка

```bash
pip install fasthttp-client
```

## Использование

```bash
fasthttp [команда] [url] [формат]
```

## Команды

### GET

```bash
fasthttp get https://api.example.com/data
```

Форматы: `status` (по умолчанию), `json`, `headers`, `text`, `all`

```bash
fasthttp get https://api.example.com/data json
```

С заголовками:

```bash
fasthttp get https://api.example.com/data json -H "Authorization: Bearer token"
```

С таймаутом:

```bash
fasthttp get https://api.example.com/data -t 10
```

### POST

Отправить JSON:

```bash
fasthttp post https://api.example.com/users json -j '{"name": "John", "age": 30}'
```

Отправить форму:

```bash
fasthttp post https://api.example.com/users json -d "name=John&age=30"
```

### PUT / PATCH / DELETE

Аналогично POST:

```bash
fasthttp put https://api.example.com/users/1 json -j '{"name": "Jane"}'
fasthttp patch https://api.example.com/users/1 json -j '{"age": 25}'
fasthttp delete https://api.example.com/users/1
```

### Версия

```bash
fasthttp version
```

## Форматы вывода

| Формат | Описание |
|--------|----------|
| `status` | Код статуса |
| `json` | JSON |
| `headers` | Заголовки |
| `text` | Текст |
| `all` | Всё |

## Ошибки

Код завершения:
- `0` — успех
- `1` — ошибка (соединение, таймаут, 4xx/5xx)

```
✗ HTTP 404
  body: {"error": "Not found"}
```

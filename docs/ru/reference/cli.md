# CLI

Справочник по командной строке.

## Использование

```bash
fasthttp <method> <url> [options] [format]
```

## Методы

| Метод | Описание |
|-------|----------|
| `get` | GET запрос |
| `post` | POST запрос |
| `put` | PUT запрос |
| `patch` | PATCH запрос |
| `delete` | DELETE запрос |

## Опции

| Опция | Кратко | Описание |
|-------|--------|----------|
| `--header` | `-H` | Добавить заголовок |
| `--param` | `-p` | Добавить параметр |
| `--json` | `-j` | JSON тело |
| `--data` | `-d` | Form данные |
| `--timeout` | `-t` | Таймаут (секунды) |
| `--debug` | - | Режим отладки |
| `--output` | `-o` | Сохранить в файл |

## Формат

| Формат | Описание |
|--------|----------|
| `status` | Только код статуса |
| `json` | JSON тело |
| `text` | Простой текст |
| `headers` | Только заголовки |
| `all` | Всё вместе |

## Примеры

```bash
# Простой GET
fasthttp get https://api.example.com/data

# С заголовками
fasthttp get https://api.example.com/data -H "Authorization: Bearer token"

# POST с JSON
fasthttp post https://api.example.com/users --json '{"name": "John"}'

# Сохранить в файл
fasthttp get https://api.example.com/data json -o response.json
```

## codegen

Генерирует fasthttp-клиент из OpenAPI 3.x спеки.

```bash
fasthttp codegen <spec> [options]
```

| Аргумент | Описание |
|----------|----------|
| `spec` | Путь или URL к OpenAPI 3.x спеке (JSON или YAML) |

| Опция | Кратко | Описание | По умолчанию |
|-------|--------|----------|--------------|
| `--output` | `-o` | Путь к выходному файлу | `client.py` |

```bash
fasthttp codegen openapi.json -o client.py
fasthttp codegen https://api.example.com/openapi.json -o client.py
```

Что генерируется и какие есть ограничения MVP — в разделе «Генерация кода»
[Команд CLI](../cli/commands.md).

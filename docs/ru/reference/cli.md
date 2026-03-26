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

# Опции CLI

Доступные опции CLI.

## Заголовки

```bash
fasthttp get https://api.example.com/data -H "Authorization: Bearer token"
```

## JSON тело

```bash
fasthttp post https://api.example.com/users --json '{"name": "John"}'
```

## Таймаут

```bash
fasthttp get https://api.example.com/data --timeout 60
```

По умолчанию: 30 секунд.

## Режим отладки

```bash
fasthttp get https://api.example.com/data --debug
```

Показывает заголовки запроса и ответа.

## Сохранение в файл

```bash
fasthttp get https://api.example.com/data json -o response.json
```

## Опции

| Опция | Кратко | Описание |
|-------|--------|----------|
| `--header` | `-H` | Добавить заголовок |
| `--param` | `-p` | Добавить параметр |
| `--json` | `-j` | JSON тело |
| `--data` | `-d` | Form данные |
| `--timeout` | `-t` | Таймаут запроса |
| `--debug` | - | Режим отладки |
| `--output` | `-o` | Сохранить в файл |

# CLI - Интерфейс командной строки

FastHTTP включает мощный интерфейс командной строки для выполнения HTTP-запросов прямо из терминала.

## Установка

Убедитесь, что пакет установлен:

```bash
pip install fasthttp-client
```

## Использование

CLI доступен через команду `fasthttp`:

```bash
fasthttp [команда] [опции]
```

## Доступные команды

### GET-запрос

Выполнить GET-запрос:

```bash
fasthttp get <url> [опции]
```

**Опции:**
- `url` - Целевой URL (обязательно)
- `output` - Формат вывода: `status`, `headers`, `json`, `text`, `all` (по умолчанию: `status`)
- `-H, --header` - Заголовки в формате `Key:Value,Key2:Value2`
- `-t, --timeout` - Таймаут запроса в секундах (по умолчанию: 30.0)

**Примеры:**

```bash
# Получить статус код
fasthttp get https://api.github.com

# Получить JSON-ответ
fasthttp get https://api.github.com/users/octocat json

# Получить полную информацию об ответе
fasthttp get https://api.github.com/users/octocat all

# С пользовательскими заголовками
fasthttp get https://api.github.com/users/octocat json -H "Authorization: Bearer token"

# С таймаутом
fasthttp get https://api.github.com -t 10
```

---

### POST-запрос

Выполнить POST-запрос:

```bash
fasthttp post <url> [опции]
```

**Опции:**
- `url` - Целевой URL (обязательно)
- `output` - Формат вывода: `status`, `headers`, `json`, `text`, `all` (по умолчанию: `status`)
- `-H, --header` - Заголовки в формате `Key:Value,Key2:Value2`
- `-j, --json` - JSON-тело
- `-d, --data` - Данные формы
- `-t, --timeout` - Таймаут запроса в секундах (по умолчанию: 30.0)

**Примеры:**

```bash
# Отправить JSON данные
fasthttp post https://api.example.com/users json -j '{"name": "John", "age": 30}'

# Отправить данные формы
fasthttp post https://api.example.com/users json -d "name=John&age=30"

# С заголовками
fasthttp post https://api.example.com/users json -j '{"name": "John"}' -H "Content-Type: application/json"
```

---

### PUT-запрос

Выполнить PUT-запрос:

```bash
fasthttp put <url> [опции]
```

**Опции:**
- `url` - Целевой URL (обязательно)
- `output` - Формат вывода: `status`, `headers`, `json`, `text`, `all` (по умолчанию: `status`)
- `-H, --header` - Заголовки в формате `Key:Value,Key2:Value2`
- `-j, --json` - JSON-тело
- `-d, --data` - Данные формы
- `-t, --timeout` - Таймаут запроса в секундах (по умолчанию: 30.0)

**Примеры:**

```bash
fasthttp put https://api.example.com/users/1 json -j '{"name": "John Updated"}'
```

---

### PATCH-запрос

Выполнить PATCH-запрос:

```bash
fasthttp patch <url> [опции]
```

**Опции:**
- `url` - Целевой URL (обязательно)
- `output` - Формат вывода: `status`, `headers`, `json`, `text`, `all` (по умолчанию: `status`)
- `-H, --header` - Заголовки в формате `Key:Value,Key2:Value2`
- `-j, --json` - JSON-тело
- `-d, --data` - Данные формы
- `-t, --timeout` - Таймаут запроса в секундах (по умолчанию: 30.0)

**Примеры:**

```bash
fasthttp patch https://api.example.com/users/1 json -j '{"age": 31}'
```

---

### DELETE-запрос

Выполнить DELETE-запрос:

```bash
fasthttp delete <url> [опции]
```

**Опции:**
- `url` - Целевой URL (обязательно)
- `output` - Формат вывода: `status`, `headers`, `json`, `text`, `all` (по умолчанию: `status`)
- `-H, --header` - Заголовки в формате `Key:Value,Key2:Value2`
- `-t, --timeout` - Таймаут запроса в секундах (по умолчанию: 30.0)

**Примеры:**

```bash
fasthttp delete https://api.example.com/users/1
fasthttp delete https://api.example.com/users/1 all -H "Authorization: Bearer token"
```

---

### Версия

Проверить версию CLI:

```bash
fasthttp version
```

Вывод:
```
FastHTTP CLI v0.1.6
```

---

## Форматы вывода

| Формат | Описание |
|--------|----------|
| `status` | Только HTTP статус-код (по умолчанию) |
| `headers` | Заголовки ответа в формате JSON |
| `body` | Тело ответа в виде текста |
| `json` | Тело ответа в формате JSON |
| `all` | Статус, время выполнения, заголовки и превью тела |

---

## Обработка ошибок

CLI возвращает код завершения 1 при ошибках:
- Ошибки подключения
- Таймауты
- HTTP-ответы 4xx/5xx

Пример вывода ошибки:
```
✗ HTTP 404
  body: {"error": "Resource not found"}
```

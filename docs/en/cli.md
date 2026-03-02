# CLI

Command-line tool for making HTTP requests directly from terminal.

## Install

```bash
pip install fasthttp-client
```

## Usage

```bash
fasthttp [command] [url] [output]
```

## Commands

### GET

Fetch data from server:

```bash
fasthttp get https://api.example.com/data
```

Output format options:
- `status` — just status code (default)
- `json` — pretty-printed JSON
- `headers` — response headers
- `text` — raw body
- `all` — everything

```bash
fasthttp get https://api.example.com/data json
```

With custom headers:

```bash
fasthttp get https://api.example.com/data json -H "Authorization: Bearer token"
```

With timeout:

```bash
fasthttp get https://api.example.com/data -t 10
```

### POST

Send JSON data:

```bash
fasthttp post https://api.example.com/users json -j '{"name": "John", "age": 30}'
```

Send form data:

```bash
fasthttp post https://api.example.com/users json -d "name=John&age=30"
```

### PUT / PATCH / DELETE

Same options as POST:

```bash
fasthttp put https://api.example.com/users/1 json -j '{"name": "Jane"}'
fasthttp patch https://api.example.com/users/1 json -j '{"age": 25}'
fasthttp delete https://api.example.com/users/1
```

### Version

Check installed version:

```bash
fasthttp version
```

## Output Formats

| Format | Description | Example |
|--------|-------------|---------|
| `status` | Just status code | `200` |
| `json` | Pretty JSON | `{"id": 1, "name": "John"}` |
| `headers` | Headers as JSON | `{"Content-Type": "application/json"}` |
| `text` | Raw text | `Hello World` |
| `all` | Everything | Status + time + headers + body |

## Headers

Pass custom headers with `-H` or `--header`:

```bash
fasthttp get https://api.example.com/data json -H "Authorization: Bearer token" -H "Accept: application/json"
```

## Timeout

Set request timeout with `-t` or `--timeout`:

```bash
fasthttp get https://slow-api.com/data -t 60
```

Default is 30 seconds.

## Errors

Exit codes:
- `0` — success
- `1` — error (connection failed, timeout, HTTP 4xx/5xx)

Error output:
```
✗ HTTP 404
  body: {"error": "Not found"}
```

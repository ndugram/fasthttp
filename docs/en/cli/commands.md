# CLI Commands

Available CLI commands.

## HTTP Methods

### GET

```bash
fasthttp get https://api.example.com/data
```

With query parameters:

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

## Output Format

Second argument determines output:

| Format | Description |
|--------|-------------|
| `status` | Status code only (default) |
| `json` | JSON response body |
| `text` | Response text |
| `headers` | Response headers |
| `all` | Everything together |

## Examples

### Status Only

```bash
$ fasthttp get https://api.example.com/data status
200
```

### JSON Response

```bash
$ fasthttp get https://api.example.com/data json
{"id": 1, "name": "John"}
```

### All Info

```bash
$ fasthttp get https://api.example.com/data all
Status: 200
Elapsed: 234.56ms
Headers: {...}
Body: {...}
```

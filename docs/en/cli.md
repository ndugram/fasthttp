# Command Line Interface (CLI)

FastHTTP comes with a convenient CLI for running requests from the terminal.

## Installation

CLI is installed with the package:

```bash
pip install fasthttp-client
```

## Basic Usage

```bash
fasthttp get https://jsonplaceholder.typicode.com/posts/1
```

## HTTP Methods

### GET

```bash
fasthttp get https://api.example.com/data
```

With query parameters in URL:

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

## Options

### Headers (-H, --header)

```bash
fasthttp get https://api.example.com/data \
  -H "Authorization: Bearer token" \
  -H "User-Agent: MyApp/1.0"
```

Multiple headers with comma:

```bash
fasthttp get https://api.example.com/data -H "Authorization: Bearer token,Content-Type: application/json"
```

### JSON Body (-j, --json)

```bash
fasthttp post https://api.example.com/users \
  --json '{"name": "John", "email": "john@example.com"}'
```

### Form Data (-d, --data)

```bash
fasthttp post https://api.example.com/login \
  --data "username=john&password=secret"
```

### Timeout (-t, --timeout)

```bash
fasthttp get https://api.example.com/data --timeout 60
```

Default is 30 seconds.

### Debug Mode (--debug)

```bash
fasthttp get https://api.example.com/data --debug
```

Shows:
- Request headers
- JSON/data body
- Response headers

## Output Format

Second argument after URL determines what to output:

### status — status only (default)

```bash
fasthttp get https://api.example.com/data status
# 200
```

### json — JSON response body

```bash
fasthttp get https://api.example.com/data json
# {"id": 1, "name": "John"}
```

### text — response text

```bash
fasthttp get https://api.example.com/data text
# <html>...</html>
```

### headers — response headers

```bash
fasthttp get https://api.example.com/data headers
# {"Content-Type": "application/json", "Date": "..."}
```

### all — everything together

```bash
fasthttp get https://api.example.com/data all
# Status: 200
# Elapsed: 234.56ms
# Headers: {...}
# Body: {...}
```

## Examples

### Simple GET

```bash
$ fasthttp get https://jsonplaceholder.typicode.com/posts/1 json
{
  "userId": 1,
  "id": 1,
  "title": "sunt aut facere repellat provident occaecati",
  "body": "..."
}
```

### POST with JSON

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

### With Headers

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

### With Debug

```bash
$ fasthttp get https://httpbin.org/get --debug
ℹ → GET https://httpbin.org/get
✔ HTTP 200 in 234.56ms
ℹ ← Response headers:
ℹ   Content-Type: application/json
ℹ   Date: Mon, 15 Jan 2025 10:30:00 GMT
```

### Check API Status

```bash
$ fasthttp get https://api.example.com/health
✔ HTTP 200 in 45.23ms
200
```

## Help

```bash
fasthttp --help
fasthttp get --help
fasthttp post --help
```

## See Also

- [Quick Start](quick-start.md) — basics
- [Configuration](configuration.md) — settings
- [Examples](examples.md) — more examples

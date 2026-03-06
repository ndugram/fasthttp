# Command Line Interface (CLI)

FastHTTP comes with a convenient CLI for running requests from the terminal.

## Installation

The CLI is installed together with the package:

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

With parameters:

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

## Parameters

### Headers

```bash
fasthttp get https://api.example.com/data \
  --header "Authorization: Bearer token" \
  --header "User-Agent: MyApp/1.0"
```

Short form:

```bash
fasthttp get https://api.example.com/data -H "Authorization: Bearer token"
```

### Query Parameters

```bash
fasthttp get https://api.example.com/search \
  --param "q=fast" \
  --param "page=1"
```

Short form:

```bash
fasthttp get https://api.example.com/search -p "q=fast" -p "page=1"
```

### Timeout

```bash
fasthttp get https://api.example.com/data --timeout 30
```

### JSON Body

```bash
fasthttp post https://api.example.com/users \
  --json '{"name": "John", "email": "john@example.com"}'
```

## Options

### Debug Mode

```bash
fasthttp get https://api.example.com/data --debug
```

### Output to File

```bash
fasthttp get https://api.example.com/data --output response.json
```

### Output Format

```bash
# JSON (default)
fasthttp get https://api.example.com/data --format json

# Status only
fasthttp get https://api.example.com/data --format status

# Body only
fasthttp get https://api.example.com/data --format body
```

## Examples

### Simple GET

```bash
$ fasthttp get https://jsonplaceholder.typicode.com/posts/1
{
  "userId": 1,
  "id": 1,
  "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
  "body": "..."
}
```

### POST with JSON

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

### With Headers

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

### With Parameters

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

## Help

```bash
fasthttp --help
```

Output:

```
usage: fasthttp [-h] [--debug] [--timeout TIMEOUT] [-H HEADER] [-p PARAM]
                [--json JSON] [--output OUTPUT] [--format FORMAT]
                method url

positional arguments:
  method                HTTP method (get, post, put, patch, delete)
  url                   Request URL

optional arguments:
  -h, --help            Show help
  --debug               Debug mode
  --timeout TIMEOUT      Timeout in seconds
  -H, --header HEADER   Header (can be multiple)
  -p, --param PARAM     Query parameter (can be multiple)
  --json JSON           JSON request body
  --output OUTPUT       Save response to file
  --format FORMAT       Output format (json, status, body)
```

## See Also

- [Quick Start](quick-start.md) — basics
- [Configuration](configuration.md) — settings
- [Examples](examples.md) — more examples

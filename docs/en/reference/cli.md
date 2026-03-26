# CLI Reference

Command line interface reference.

## Usage

```bash
fasthttp <method> <url> [options] [format]
```

## Methods

| Method | Description |
|--------|-------------|
| `get` | GET request |
| `post` | POST request |
| `put` | PUT request |
| `patch` | PATCH request |
| `delete` | DELETE request |

## Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--header` | `-H` | Add header | - |
| `--param` | `-p` | Add query param | - |
| `--json` | `-j` | JSON body | - |
| `--data` | `-d` | Form data | - |
| `--timeout` | `-t` | Timeout (seconds) | 30 |
| `--debug` | - | Debug mode | false |
| `--output` | `-o` | Save to file | - |

## Format

| Format | Description |
|--------|-------------|
| `status` | Status code only |
| `json` | JSON body |
| `text` | Plain text |
| `headers` | Headers only |
| `all` | Everything |

## Examples

```bash
# Simple GET
fasthttp get https://api.example.com/data

# With headers
fasthttp get https://api.example.com/data -H "Authorization: Bearer token"

# POST with JSON
fasthttp post https://api.example.com/users --json '{"name": "John"}'

# With timeout
fasthttp get https://api.example.com/data --timeout 60

# Save to file
fasthttp get https://api.example.com/data json -o response.json

# Debug mode
fasthttp get https://api.example.com/data --debug
```

## Help

```bash
fasthttp --help
fasthttp get --help
fasthttp post --help
```

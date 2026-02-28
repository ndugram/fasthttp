# CLI - Command Line Interface

FastHTTP includes a powerful command-line interface for making HTTP requests directly from your terminal.

## Installation

Make sure the package is installed:

```bash
pip install fasthttp-client
```

## Usage

The CLI is available via the `fasthttp` command:

```bash
fasthttp [command] [options]
```

## Available Commands

### GET Request

Perform a GET request:

```bash
fasthttp get <url> [options]
```

**Options:**
- `url` - Target URL (required)
- `output` - Output format: `status`, `headers`, `json`, `text`, `all` (default: `status`)
- `-H, --header` - Headers in format `Key:Value,Key2:Value2`
- `-t, --timeout` - Request timeout in seconds (default: 30.0)

**Examples:**

```bash
# Get status code
fasthttp get https://api.github.com

# Get JSON response
fasthttp get https://api.github.com/users/octocat json

# Get full response details
fasthttp get https://api.github.com/users/octocat all

# With custom headers
fasthttp get https://api.github.com/users/octocat json -H "Authorization: Bearer token"

# With timeout
fasthttp get https://api.github.com -t 10
```

---

### POST Request

Perform a POST request:

```bash
fasthttp post <url> [options]
```

**Options:**
- `url` - Target URL (required)
- `output` - Output format: `status`, `headers`, `json`, `text`, `all` (default: `status`)
- `-H, --header` - Headers in format `Key:Value,Key2:Value2`
- `-j, --json` - JSON body
- `-d, --data` - Form data
- `-t, --timeout` - Request timeout in seconds (default: 30.0)

**Examples:**

```bash
# Post JSON data
fasthttp post https://api.example.com/users json -j '{"name": "John", "age": 30}'

# Post form data
fasthttp post https://api.example.com/users json -d "name=John&age=30"

# With headers
fasthttp post https://api.example.com/users json -j '{"name": "John"}' -H "Content-Type: application/json"
```

---

### PUT Request

Perform a PUT request:

```bash
fasthttp put <url> [options]
```

**Options:**
- `url` - Target URL (required)
- `output` - Output format: `status`, `headers`, `json`, `text`, `all` (default: `status`)
- `-H, --header` - Headers in format `Key:Value,Key2:Value2`
- `-j, --json` - JSON body
- `-d, --data` - Form data
- `-t, --timeout` - Request timeout in seconds (default: 30.0)

**Examples:**

```bash
fasthttp put https://api.example.com/users/1 json -j '{"name": "John Updated"}'
```

---

### PATCH Request

Perform a PATCH request:

```bash
fasthttp patch <url> [options]
```

**Options:**
- `url` - Target URL (required)
- `output` - Output format: `status`, `headers`, `json`, `text`, `all` (default: `status`)
- `-H, --header` - Headers in format `Key:Value,Key2:Value2`
- `-j, --json` - JSON body
- `-d, --data` - Form data
- `-t, --timeout` - Request timeout in seconds (default: 30.0)

**Examples:**

```bash
fasthttp patch https://api.example.com/users/1 json -j '{"age": 31}'
```

---

### DELETE Request

Perform a DELETE request:

```bash
fasthttp delete <url> [options]
```

**Options:**
- `url` - Target URL (required)
- `output` - Output format: `status`, `headers`, `json`, `text`, `all` (default: `status`)
- `-H, --header` - Headers in format `Key:Value,Key2:Value2`
- `-t, --timeout` - Request timeout in seconds (default: 30.0)

**Examples:**

```bash
fasthttp delete https://api.example.com/users/1
fasthttp delete https://api.example.com/users/1 all -H "Authorization: Bearer token"
```

---

### Version

Check CLI version:

```bash
fasthttp version
```

Output:
```
FastHTTP CLI v0.1.6
```

---

## Output Formats

| Format | Description |
|--------|-------------|
| `status` | HTTP status code only (default) |
| `headers` | Response headers as JSON |
| `body` | Response body as text |
| `json` | Response body parsed as JSON |
| `all` | Status, elapsed time, headers, and body preview |

---

## Error Handling

The CLI returns exit code 1 on errors:
- Connection failures
- Timeouts
- HTTP 4xx/5xx responses

Example error output:
```
✗ HTTP 404
  body: {"error": "Resource not found"}
```

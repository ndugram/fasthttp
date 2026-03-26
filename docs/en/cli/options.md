# CLI Options

Available CLI options.

## Headers

```bash
fasthttp get https://api.example.com/data \
  -H "Authorization: Bearer token" \
  -H "User-Agent: MyApp/1.0"
```

Multiple headers:

```bash
fasthttp get https://api.example.com/data -H "Authorization: Bearer token,Content-Type: application/json"
```

## JSON Body

```bash
fasthttp post https://api.example.com/users \
  --json '{"name": "John", "email": "john@example.com"}'
```

## Form Data

```bash
fasthttp post https://api.example.com/login \
  --data "username=john&password=secret"
```

## Timeout

```bash
fasthttp get https://api.example.com/data --timeout 60
```

Default: 30 seconds.

## Debug Mode

```bash
fasthttp get https://api.example.com/data --debug
```

Shows:

- Request headers
- JSON/data body
- Response headers

## Query Parameters

```bash
fasthttp get "https://api.example.com/search?q=test" -p "page=1" -p "limit=10"
```

## Save to File

```bash
fasthttp get https://api.example.com/data json -o response.json
```

## Options Summary

| Option | Short | Description |
|--------|-------|-------------|
| `--header` | `-H` | Add header |
| `--param` | `-p` | Add query parameter |
| `--json` | `-j` | JSON body |
| `--data` | `-d` | Form data |
| `--timeout` | `-t` | Request timeout |
| `--debug` | - | Debug mode |
| `--output` | `-o` | Save to file |
| `--format` | - | Output format |

# Logging

Configure logging and debug mode.

## Debug Mode

```python
# Verbose output - all headers, body, time
app = FastHTTP(debug=True)

# Minimal output - status and time only
app = FastHTTP(debug=False)
```

## Debug Output

When `debug=True`:

```
DEBUG   | fasthttp    | GET https://api.example.com/data | headers={'User-Agent': 'fasthttp/0.1.0'}
DEBUG   | fasthttp    | 200 | headers={'Content-Type': 'application/json'}
INFO    | fasthttp    | GET https://api.example.com/data 200 150.23ms
```

When `debug=False`:

```
INFO    | fasthttp    | GET https://api.example.com/data 200 150.23ms
```

## What Debug Shows

### debug=True
- Request and response headers
- Request and response body
- Execution time of each request
- Full URL with parameters

### debug=False
- Only status code
- Execution time

## Example

```python
from fasthttp import FastHTTP

app = FastHTTP(debug=True)


@app.get(url="https://api.example.com/data")
async def handler(resp):
    return resp.json()


app.run()
```

## Logging Best Practices

- Use `debug=True` during development
- Use `debug=False` in production
- Check logs regularly for errors
- Monitor request times

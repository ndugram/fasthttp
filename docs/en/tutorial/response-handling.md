# Response Handling

Learn how to work with HTTP responses.

## Accessing Response Data

```python
@app.get(url="https://api.example.com/data")
async def handle_response(resp: Response) -> dict:
    # Status code (200, 404, 500, etc.)
    status = resp.status
    
    # JSON body
    data = resp.json()
    
    # Text response
    text = resp.text
    
    # Response headers
    headers = resp.headers
    
    # Raw content
    content = resp.content
    
    return {"status": status, "data": data}
```

## Response Methods

### json()

Parses response body as JSON:

```python
data = resp.json()  # Returns dict or list
```

### text

Returns raw text:

```python
text = resp.text  # Returns str
```

### req_json()

Returns the JSON that was sent with the request:

```python
# For POST request with json={"name": "John"}
sent = resp.req_json()  # Returns {"name": "John"}
```

### req_text()

Returns request body as text:

```python
# For POST request with data=b"raw data"
sent = resp.req_text()  # Returns "raw data"
```

## Error Handling

FastHTTP automatically handles errors and logs them:

```python
@app.get(url="https://httpbin.org/status/404")
async def handle_error(resp: Response) -> dict:
    return {"status": resp.status}


@app.get(url="https://httpbin.org/status/500")
async def handle_server_error(resp: Response) -> dict:
    return {"status": resp.status}
```

### Checking for Errors

```python
@app.get(url="https://api.example.com/data")
async def check_response(resp: Response) -> dict | None:
    if resp is None:
        return {"error": "Request failed"}
    
    if resp.status >= 400:
        return {"error": f"HTTP {resp.status}"}
    
    return resp.json()
```

## Response Properties

| Property | Type | Description |
|----------|------|-------------|
| `status` | `int` | HTTP status code |
| `text` | `str` | Raw response body |
| `headers` | `dict` | Response headers |
| `content` | `bytes` | Raw bytes |
| `method` | `str` | HTTP method used |

## Complete Example

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)


@app.get(url="https://api.example.com/data")
async def handler(resp: Response) -> dict:
    return {
        "status": resp.status,
        "data": resp.json(),
        "headers": resp.headers,
    }


if __name__ == "__main__":
    app.run()
```

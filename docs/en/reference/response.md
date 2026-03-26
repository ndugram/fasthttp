# Response Class

Response object reference.

## Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `status` | `int` | HTTP status code |
| `text` | `str` | Raw response body |
| `headers` | `dict` | Response headers |
| `content` | `bytes` | Raw bytes |
| `method` | `str` | HTTP method |

## Methods

### json()

Parse response body as JSON:

```python
data = resp.json()  # Returns dict or list
```

### req_json()

Get JSON sent with request:

```python
sent = resp.req_json()  # Returns dict or None
```

### req_text()

Get request body as text:

```python
sent = resp.req_text()  # Returns str or None
```

## Example

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
```

## Handling Errors

```python
@app.get(url="https://api.example.com/data")
async def handler(resp: Response) -> dict | None:
    if resp is None:
        return {"error": "Request failed"}
    
    return {"status": resp.status, "data": resp.json()}
```

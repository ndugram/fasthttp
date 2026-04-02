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
| `url` | `str` | Request URL |

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

### assets()

Extract CSS and JavaScript asset URLs from HTML response:

```python
result = resp.assets()
# Returns: {"css": [...], "js": [...]}
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `css` | `bool` | `True` | Include CSS links |
| `js` | `bool` | `True` | Include JavaScript links |

**Examples:**

```python
# Get all assets (CSS + JS)
@app.get(url="https://example.com")
async def handler(resp: Response):
    return resp.assets()
# Returns: {"css": ["https://example.com/style.css"], "js": ["https://example.com/app.js"]}

# CSS only
@app.get(url="https://example.com")
async def handler(resp: Response):
    return resp.assets(js=False)
# Returns: {"css": [...], "js": []}

# JS only
@app.get(url="https://example.com")
async def handler(resp: Response):
    return resp.assets(css=False)
# Returns: {"css": [], "js": [...]}
```

The method parses `<link rel="stylesheet" href="...">` for CSS and `<script src="...">` for JavaScript. All URLs are normalized using `urljoin`, so relative paths are converted to absolute URLs based on the request URL.

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

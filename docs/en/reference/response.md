# Response Class

Response object reference.

## Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `status` | `int` | HTTP status code |
| `text` | `str` | Raw response body as string |
| `headers` | `dict` | Response headers |
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

### bytes()

Returns the raw response body as bytes. Uses the actual bytes received from the server; falls back to `text.encode()` if unavailable:

```python
raw = resp.bytes()  # Returns bytes
```

**Use cases:** downloading images, PDFs, zip files, any binary content.

```python
@app.get(url="https://httpbin.org/image/png")
async def handler(resp: Response) -> dict:
    raw = resp.bytes()
    return {"size": len(raw), "is_png": raw[:4] == b"\x89PNG"}
```

### html()

Returns the response body as an HTML string. Raises `ValueError` if `Content-Type` is not HTML:

```python
html = resp.html()  # Returns str
```

**Raises:** `ValueError` — if `Content-Type` is present and does not contain `html`.

```python
@app.get(url="https://example.com")
async def handler(resp: Response) -> dict:
    html = resp.html()
    return {"length": len(html)}
```

### xml()

Parses the response body as XML and returns the root `xml.etree.ElementTree.Element`:

```python
root = resp.xml()  # Returns ET.Element
```

**Raises:** `xml.etree.ElementTree.ParseError` — if the body is not valid XML.

```python
@app.get(url="https://feeds.bbci.co.uk/news/rss.xml")
async def handler(resp: Response) -> dict:
    root = resp.xml()
    channel = root.find("channel")
    return {"title": channel.findtext("title")}
```

!!! warning
    Uses the stdlib XML parser — vulnerable to XXE attacks. Only use with trusted sources.

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

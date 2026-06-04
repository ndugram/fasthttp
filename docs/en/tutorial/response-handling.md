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
    
    # Raw bytes
    raw = resp.bytes()
    
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

### bytes()

Returns the raw response body as bytes. Use for binary responses like images, PDFs, or archives:

```python
@app.get(url="https://httpbin.org/image/png")
async def download_image(resp: Response) -> dict:
    raw = resp.bytes()
    return {
        "size": len(raw),
        "is_png": raw[:4] == b"\x89PNG",
    }
```

### html()

Returns the response body as an HTML string. Raises `ValueError` if the `Content-Type` is not HTML — useful to catch accidental calls on JSON endpoints:

```python
@app.get(url="https://example.com")
async def get_page(resp: Response) -> dict:
    html = resp.html()
    return {"length": len(html)}
```

```python
# Raises ValueError: Expected HTML response, got Content-Type: application/json
@app.get(url="https://api.example.com/users")
async def wrong_call(resp: Response):
    return resp.html()
```

### xml()

Parses the response body as XML and returns the root `Element`. Works for any XML-based format including RSS and Atom feeds:

```python
@app.get(url="https://feeds.bbci.co.uk/news/rss.xml")
async def get_rss(resp: Response) -> dict:
    root = resp.xml()
    channel = root.find("channel")
    items = channel.findall("item")
    return {
        "feed": channel.findtext("title"),
        "count": len(items),
        "latest": [i.findtext("title") for i in items[:3]],
    }
```

!!! warning
    `xml()` uses the standard library XML parser which is vulnerable to entity expansion attacks (XXE). Only use it with **trusted sources**. For untrusted data, use `defusedxml`.

### assets()

Extracts CSS and JavaScript asset URLs from HTML page:

```python
# Get all assets
result = resp.assets()
# Returns: {"css": [...], "js": [...]}

# CSS only
css_only = resp.assets(js=False)

# JS only
js_only = resp.assets(css=False)
```

The method parses:
- CSS: `<link rel="stylesheet" href="...">` tags
- JS: `<script src="...">` tags

All URLs are normalized relative to the request URL.

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

### raise_for_status

By default, 4xx and 5xx responses are logged and the handler receives `None`. Enable `raise_for_status` to raise `FastHTTPBadStatusError` instead.

#### Global — all routes

```python
from fasthttp import FastHTTP
from fasthttp.exceptions import FastHTTPBadStatusError
from fasthttp.response import Response

app = FastHTTP(raise_for_status=True)


@app.get(url="https://api.example.com/users")
async def get_users(resp: Response) -> list:
    return resp.json()


if __name__ == "__main__":
    try:
        app.run()
    except FastHTTPBadStatusError as e:
        print(f"HTTP {e.status_code} on {e.url}")
```

#### Per-route — only specific routes

```python
app = FastHTTP()


@app.get(url="https://api.example.com/critical", raise_for_status=True)
async def critical(resp: Response) -> dict:
    return resp.json()


@app.get(url="https://api.example.com/optional")
async def optional(resp: Response) -> dict | None:
    if resp is None:
        return None
    return resp.json()
```

`FastHTTPBadStatusError` has `.status_code`, `.url`, `.method`, and `.response_body` attributes.

## Response Properties

| Property | Type | Description |
|----------|------|-------------|
| `status` | `int` | HTTP status code |
| `text` | `str` | Raw response body |
| `headers` | `dict` | Response headers |
| `bytes()` | `bytes` | Raw response body as bytes |
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

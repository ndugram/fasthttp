# File Uploads

FastHTTP supports multipart file uploads via the `files` parameter.

## Simple Upload

Pass bytes directly:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.post(
    url="https://api.example.com/upload",
    files={"file": b"Hello, world!"},
)
async def upload(resp: Response) -> dict:
    return resp.json()
```

## Upload with Filename and Content Type

Provide a tuple of `(filename, data, content_type)`:

```python
@app.post(
    url="https://api.example.com/upload",
    files={"file": ("report.csv", b"name,score\nAlice,95\n", "text/csv")},
)
async def upload_csv(resp: Response) -> dict:
    return resp.json()
```

## Multiple Files

Pass a dictionary with multiple keys:

```python
@app.post(
    url="https://api.example.com/upload",
    files={
        "avatar": ("photo.jpg", b"\xff\xd8\xff\xe0...", "image/jpeg"),
        "document": ("resume.pdf", b"%PDF-1.4...", "application/pdf"),
    },
)
async def upload_multi(resp: Response) -> dict:
    return resp.json()
```

Or use a list to send multiple files under the same field name:

```python
@app.post(
    url="https://api.example.com/upload",
    files=[
        ("files", ("a.txt", b"content of a", "text/plain")),
        ("files", ("b.txt", b"content of b", "text/plain")),
    ],
)
async def upload_list(resp: Response) -> dict:
    return resp.json()
```

## Upload with JSON

Combine `files` with `json` to send metadata alongside the file:

```python
@app.post(
    url="https://api.example.com/upload",
    json={"title": "My photo", "tags": ["nature"]},
    files={"file": ("sunset.jpg", b"\xff\xd8\xff\xe0...", "image/jpeg")},
)
async def upload_with_meta(resp: Response) -> dict:
    return resp.json()
```

## File Object

Pass an open file handle:

```python
@app.post(
    url="https://api.example.com/upload",
    files={"file": open("photo.jpg", "rb")},
)
async def upload_file(resp: Response) -> dict:
    return resp.json()
```

## Path Object

Pass a `pathlib.Path`:

```python
from pathlib import Path

FILE = Path("photo.jpg")


@app.post(
    url="https://api.example.com/upload",
    files={"file": FILE},
)
async def upload_path(resp: Response) -> dict:
    return resp.json()
```

## Supported Types

The `files` parameter accepts:

| Type | Example |
|------|---------|
| `bytes` | `b"raw data"` |
| `str` | `"text content"` |
| file object | `open("file.txt", "rb")` |
| `Path` | `Path("file.txt")` |
| tuple `(name, data)` | `("file.txt", b"data")` |
| tuple `(name, data, type)` | `("file.txt", b"data", "text/plain")` |
| dict `name -> data` | `{"file": b"data"}` |
| dict `name -> tuple` | `{"file": ("f.txt", b"data")}` |
| list of tuples | `[("f", b"a"), ("f", b"b")]` |

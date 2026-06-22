# Загрузка файлов

FastHTTP поддерживает загрузку файлов через multipart/form-data с помощью параметра `files`.

## Простая загрузка

Передайте байты напрямую:

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

## Загрузка с именем файла и типом контента

Передайте кортеж `(имя_файла, данные, тип_контента)`:

```python
@app.post(
    url="https://api.example.com/upload",
    files={"file": ("report.csv", b"name,score\nAlice,95\n", "text/csv")},
)
async def upload_csv(resp: Response) -> dict:
    return resp.json()
```

## Несколько файлов

Передайте словарь с несколькими ключами:

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

Или используйте список для отправки нескольких файлов под одним именем поля:

```python
@app.post(
    url="https://api.example.com/upload",
    files=[
        ("files", ("a.txt", b"содержимое a", "text/plain")),
        ("files", ("b.txt", b"содержимое b", "text/plain")),
    ],
)
async def upload_list(resp: Response) -> dict:
    return resp.json()
```

## Загрузка с JSON

Сочетайте `files` с `json` для отправки метаданных вместе с файлом:

```python
@app.post(
    url="https://api.example.com/upload",
    json={"title": "Моё фото", "tags": ["природа"]},
    files={"file": ("sunset.jpg", b"\xff\xd8\xff\xe0...", "image/jpeg")},
)
async def upload_with_meta(resp: Response) -> dict:
    return resp.json()
```

## Файловый объект

Передайте открытый файловый дескриптор:

```python
@app.post(
    url="https://api.example.com/upload",
    files={"file": open("photo.jpg", "rb")},
)
async def upload_file(resp: Response) -> dict:
    return resp.json()
```

## Path объект

Передайте `pathlib.Path`:

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

## Поддерживаемые типы

Параметр `files` принимает:

| Тип | Пример |
|-----|--------|
| `bytes` | `b"данные"` |
| `str` | `"текст"` |
| файловый объект | `open("file.txt", "rb")` |
| `Path` | `Path("file.txt")` |
| кортеж `(имя, данные)` | `("file.txt", b"data")` |
| кортеж `(имя, данные, тип)` | `("file.txt", b"data", "text/plain")` |
| словарь `имя -> данные` | `{"file": b"data"}` |
| словарь `имя -> кортеж` | `{"file": ("f.txt", b"data")}` |
| список кортежей | `[("f", b"a"), ("f", b"b")]` |

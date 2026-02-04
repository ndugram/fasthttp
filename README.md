# FastHTTP Client

<div align="center">

![aiohttp](https://img.shields.io/badge/aiohttp-3.13.3-blue.svg)
![ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)
![mypy](https://img.shields.io/badge/type%20checked-mypy-2E5090.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**🚀 Simple & Fast HTTP Client for Python**

[Documentation](docs/en/index.md) • [Quick Start](docs/en/quick-start.md) • [Examples](docs/en/examples.md)

</div>

## ⚡ Features

- **Simple API** - Minimal boilerplate with decorators
- **Beautiful Logging** - Colorful request/response logs with timing
- **Async Support** - Built on aiohttp for high performance
- **Type Safe** - Full type annotations
- **All HTTP Methods** - GET, POST, PUT, PATCH, DELETE

## 🚀 Quick Start

### Installation
```bash
pip install fasthttp-client
```

### Basic Usage
```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.get(url="https://httpbin.org/get")
async def get_data(resp: Response):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

**Output:**
```
16:09:18.955 │ INFO     │ fasthttp │ ✔ FastHTTP started
16:09:19.519 │ INFO     │ fasthttp │ ✔ ← GET https://httpbin.org/get [200] 458.26ms
16:09:20.037 │ INFO     │ fasthttp │ ✔ Done in 1.08s
```

### With Configuration
```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(
    debug=True,
    get_request={
        "headers": {"User-Agent": "MyApp/1.0"},
        "timeout": 10,
    },
)

@app.get(url="https://api.github.com/users/octocat")
async def get_user(resp: Response):
    return resp.json()

if __name__ == "__main__":
    app.run()
```

## 🔧 All HTTP Methods

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()

# GET
@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def get_post(resp: Response):
    return resp.json()

# POST
@app.post(url="https://httpbin.org/post", json={"name": "John"})
async def create_user(resp: Response):
    return f"Created: {resp.status}"

# PUT
@app.put(url="https://httpbin.org/put", json={"name": "Jane"})
async def update_user(resp: Response):
    return resp.json()

# DELETE
@app.delete(url="https://httpbin.org/delete")
async def delete_user(resp: Response):
    return f"Delete: {resp.status}"
```

## 📚 Documentation

- **[📖 Documentation](docs/index.md)** - Complete guide
- **[⚡ Quick Start](docs/quick-start.md)** - Get started in 2 minutes
- **[🔧 API Reference](docs/api-reference.md)** - Full API documentation
- **[💡 Examples](docs/examples.md)** - Real-world examples
- **[⚙️ Configuration](docs/configuration.md)** - Advanced settings

## 🛠️ Development

```bash
git clone https://github.com/ndugram/fasthttp.git
cd fasthttp
pip install -e ".[dev]"

# Run tests
pytest

# Code quality
ruff format .
ruff check .
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## 🔒 Security

See [SECURITY.md](SECURITY.md) for security policies.

---

**Made with ❤️ by the NDUgram Team**

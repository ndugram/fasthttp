# FastHTTP Client

<div align="center">

![PyPI version](https://badge.fury.io/py/fasthttp.svg)
![Python Version](https://img.shields.io/pypi/pyversions/fasthttp.svg)
![License](https://img.shields.io/pypi/l/fasthttp.svg)
![aiohttp](https://img.shields.io/badge/aiohttp-3.13.3-green.svg)
![Tests](https://github.com/ndugram/fasthttp/workflows/Tests/badge.svg)
![Code Style](https://img.shields.io/badge/code%20style-ruff-000000.svg)
![Type Checked](https://img.shields.io/badge/type%20checked-mypy-2E5090.svg)

**🚀 Fast & Simple HTTP Client Library with Async Support & Beautiful Logging**

[Documentation](docs/index.md) • [Quick Start](#quick-start) • [API Reference](docs/api-reference.md) • [Examples](docs/examples.md)

</div>

## ✨ Features

- ⚡ **Lightning Fast** - Built on aiohttp for high performance async operations
- 🎨 **Beautiful Logging** - Detailed request/response logging with timing and colors
- 🛡️ **Type Safe** - Full type annotations for better development experience  
- 🔧 **Simple API** - Minimal boilerplate with decorator-based route registration
- 📊 **Rich Output** - Colored logs with emojis and structured formatting
- 🔄 **All HTTP Methods** - GET, POST, PUT, PATCH, DELETE support
- ⚙️ **Flexible Config** - Global and per-request configuration options
- 🐍 **Modern Python** - Compatible with Python 3.10+

## Features

- 🚀 **Fast & Simple** - Easy-to-use HTTP client with minimal boilerplate
- 🔄 **Async Support** - Built on top of aiohttp for high performance
- 📊 **Beautiful Logging** - Detailed request/response logging with timing
- 🛡️ **Type Safe** - Full type annotations for better developer experience
- 🔧 **Flexible** - Support for all HTTP methods (GET, POST, PUT, PATCH, DELETE)
- ⚡ **Modern Python** - Compatible with Python 3.10+

## 🚀 Quick Start

### Installation

```bash
pip install fasthttp
```

### Your First Request

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

# Create the app
app = FastHTTP()

# Register a GET request  
@app.get(url="https://httpbin.org/get")
async def get_data(resp: Response):
    return resp.json()

# Run all requests
if __name__ == "__main__":
    app.run()
```

**Output:**
```
16:09:18.955 │ INFO     │ fasthttp │ ✔ FastHTTP started
16:09:19.519 │ INFO     │ fasthttp │ ✔ ← GET https://httpbin.org/get [200] 458.26ms
16:09:19.520 │ DEBUG    │ fasthttp │ ↳ {"args": {}, "headers": {...}, "url": "https://httpbin.org/get"}
16:09:20.037 │ INFO     │ fasthttp │ ✔ Done in 1.08s
```

### With Configuration

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(
    debug=True,
    get_request={
        "headers": {
            "User-Agent": "MyApp/1.0",
            "Authorization": "Bearer your-token",
        },
        "timeout": 10,
    },
)

@app.get(url="https://api.github.com/users/octocat")
async def get_user(resp: Response):
    user_data = resp.json()
    return f"👤 {user_data['name']} - {user_data['bio']}"

if __name__ == "__main__":
    app.run()
```

## 🔧 All HTTP Methods

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()

# GET Request
@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def get_post(resp: Response):
    return resp.json()

# POST Request with JSON
@app.post(url="https://httpbin.org/post", json={"name": "John", "age": 30})
async def create_user(resp: Response):
    return f"✅ Created: {resp.status}"

# PUT Request
@app.put(url="https://httpbin.org/put", json={"name": "Jane", "age": 25})
async def update_user(resp: Response):
    return resp.json()

# PATCH Request  
@app.patch(url="https://httpbin.org/patch", json={"age": 26})
async def patch_user(resp: Response):
    return resp.status

# DELETE Request
@app.delete(url="https://httpbin.org/delete")
async def delete_user(resp: Response):
    return f"🗑️ Delete status: {resp.status}"

if __name__ == "__main__":
    app.run()
```

## 📊 Rich Response Handling

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()

@app.get(url="https://api.github.com/user")
async def github_profile(resp: Response):
    if resp.status == 200:
        user = resp.json()
        return f"""
🐙 GitHub Profile:
👤 Name: {user.get('name', 'N/A')}
📧 Email: {user.get('email', 'N/A')}
📊 Public Repos: {user.get('public_repos', 0)}
⭐ Followers: {user.get('followers', 0)}
"""
    return f"❌ Error: {resp.status}"

@app.post(url="https://httpbin.org/post", json={"test": "data"})
async def post_with_validation(resp: Response):
    if resp.status == 200:
        return f"✅ Success: {resp.json()['json']}"
    return f"❌ Failed: {resp.status}"

if __name__ == "__main__":
    app.run()
```

## 🎨 Beautiful Logging

Enable debug mode for detailed insights:

```python
app = FastHTTP(debug=True)

# Shows:
# 🐛 Route registration
# 📤 Request details with headers  
# 📥 Response with timing
# 📊 Handler results
# ⏱️ Performance metrics
```

**Debug Output:**
```
16:09:18.954 │ DEBUG    │ fasthttp │ 🐛 Registered route: GET https://api.github.com/user
16:09:19.519 │ DEBUG    │ fasthttp │ 🐛 → GET https://api.github.com/user | headers={'Authorization': '...'}
16:09:19.866 │ INFO     │ fasthttp │ ✔ ← GET https://api.github.com/user [200] 347.26ms
16:09:19.867 │ DEBUG    │ fasthttp │ ↳ 🐙 GitHub Profile: Name: John Doe
16:09:20.037 │ INFO     │ fasthttp │ ✔ Done in 1.08s
```

## 🏆 Why Choose FastHTTP?

| Feature | FastHTTP | aiohttp | requests | httpx |
|---------|----------|---------|----------|-------|
| **Simple API** | ✅ | ❌ | ✅ | ❌ |
| **Beautiful Logging** | ✅ | ❌ | ❌ | ❌ |
| **Type Safety** | ✅ | ❌ | ❌ | ✅ |
| **Decorator Routes** | ✅ | ❌ | ❌ | ❌ |
| **Async Support** | ✅ | ✅ | ❌ | ✅ |
| **Zero Boilerplate** | ✅ | ❌ | ✅ | ❌ |

### vs requests
```python
# requests (verbose)
import requests

response = requests.get('https://api.example.com/data', headers=headers)
if response.status_code == 200:
    data = response.json()
    print(f"✅ Success: {data}")

# FastHTTP (clean & beautiful)
@app.get(url="https://api.example.com/data")
async def handler(resp: Response):
    return resp.json()  # Beautiful logging included!
```

### vs aiohttp (complex)
```python
# aiohttp (complex setup)
async with aiohttp.ClientSession() as session:
    async with session.get('https://api.example.com/data') as response:
        data = await response.json()

# FastHTTP (simple & elegant)
@app.get(url="https://api.example.com/data")
async def handler(resp: Response):
    return resp.json()
```

## 📈 Performance

FastHTTP is built on aiohttp for maximum performance:

- ⚡ **Async/Await** - Non-blocking I/O operations
- 🚀 **Connection Pooling** - Efficient connection reuse
- 📊 **Request Batching** - Multiple requests run concurrently
- ⏱️ **Smart Delays** - Automatic delays to avoid overwhelming servers

```python
# Run 10 requests concurrently - all start at once!
for i in range(10):
    @app.get(url=f"https://api.example.com/data/{i}")
    async def handler(resp: Response, i=i):
        return f"Request {i}: {resp.status}"

app.run()  # All 10 requests execute concurrently
```

## 📚 Complete Documentation

Our documentation covers everything you need:

### 📖 [Documentation Home](docs/index.md)
Complete guide and overview

### ⚡ [Quick Start](docs/quick-start.md)  
Get up and running in 2 minutes

### 🔧 [API Reference](docs/api-reference.md)
Detailed API documentation for all classes and methods

### 💡 [Examples](docs/examples.md)
Real-world examples and use cases

### ⚙️ [Configuration](docs/configuration.md)
Advanced configuration options and patterns

## 🛠️ Common Use Cases

### API Testing & Development
```python
# Perfect for API testing
app = FastHTTP(debug=True)

@app.get(url="https://api.github.com/user")
async def test_auth(resp: Response):
    assert resp.status == 200
    user = resp.json()
    assert 'login' in user
    return "✅ Auth working"

@app.post(url="https://api.example.com/users", json={"name": "test"})
async def test_create(resp: Response):
    assert resp.status in [200, 201]
    return "✅ Create working"
```

### Microservice Communication
```python
# Lightweight service communication
app = FastHTTP(
    get_request={
        "headers": {"X-Service": "user-service"},
        "timeout": 5,
    }
)

@app.get(url="http://auth-service:8080/validate")
async def validate_token(resp: Response):
    return resp.status == 200
```

### Web Scraping & Monitoring
```python
# Simple monitoring script
app = FastHTTP(get_request={"timeout": 10})

@app.get(url="https://your-app.com/health")
async def health_check(resp: Response):
    if resp.status == 200:
        return "✅ Service healthy"
    return f"❌ Service down: {resp.status}"
```

## 🛠️ Development & Contributing

### Quick Setup

```bash
git clone https://github.com/ndugram/fasthttp.git
cd fasthttp

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Code quality
ruff format .
ruff check .
mypy fasthttp/
```

### Project Structure

```
fasthttp/
├── fasthttp/
│   ├── __init__.py          # Main exports
│   ├── app.py              # FastHTTP class
│   ├── client.py           # HTTP client logic
│   ├── response.py         # Response class
│   ├── routing.py          # Route management
│   ├── logging.py          # Logging setup
│   └── types.py            # Type definitions
├── docs/                   # Documentation
│   ├── index.md           # Main docs
│   ├── quick-start.md     # Quick start guide
│   ├── api-reference.md   # API reference
│   ├── examples.md        # Usage examples
│   └── configuration.md   # Configuration guide
├── examples/               # Example scripts
├── tests/                 # Test suite
├── pyproject.toml         # Project configuration
└── README.md              # This file
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=fasthttp --cov-report=html

# Run specific test categories
pytest tests/test_client.py -v
pytest -m "not slow"  # Skip slow tests

# Debug mode
pytest --pdb tests/test_client.py
```

### Code Quality Tools

```bash
# Format code (automatic)
ruff format .

# Lint code (find issues)
ruff check .

# Type checking
mypy fasthttp/

# All checks at once
ruff format . && ruff check . && mypy fasthttp/
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes with tests
4. **Run** quality checks: `ruff format . && ruff check . && mypy fasthttp && pytest`
5. **Commit** your changes: `git commit -m "Add amazing feature"`
6. **Push** to branch: `git push origin feature/amazing-feature`
7. **Open** a Pull Request

### Contribution Guidelines

- ✅ Write tests for new features
- ✅ Follow existing code style (ruff formatting)
- ✅ Add type annotations
- ✅ Update documentation for new features
- ✅ Keep commits focused and descriptive

### Development Workflow

```bash
# Setup pre-commit hooks (recommended)
pip install pre-commit
pre-commit install

# Now ruff and mypy run automatically on git commit!
git commit -m "Add feature"  # Auto-formats and checks code
```

## 📄 License & Support

### License
MIT License - see [LICENSE](LICENSE) file for details.

### Support & Community

- 🐛 **Issues**: [GitHub Issues](https://github.com/ndugram/fasthttp/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/ndugram/fasthttp/discussions)
- 📖 **Documentation**: [Complete Docs](docs/index.md)
- ✨ **Examples**: [Usage Examples](docs/examples.md)

### Changelog
See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

---

<div align="center">

**Made with ❤️ by the FastHTTP Team**

[⬆ Back to Top](#fasthttp-client)

</div>


# FastHTTP Client Documentation

Welcome to the FastHTTP Client documentation! This guide will help you get started with our fast and simple HTTP client library.

## 📚 Documentation Structure

- [Quick Start](quick-start.md) - Get up and running in 2 minutes
- [API Reference](api-reference.md) - Complete API documentation  
- [Examples](examples.md) - Real-world usage examples
- [Configuration](configuration.md) - Advanced configuration options

## 🚀 What is FastHTTP Client?

FastHTTP Client is a modern, async HTTP client library built on top of aiohttp. It provides:

- **Simple API** - Minimal boilerplate for HTTP requests
- **Beautiful Logging** - Detailed request/response logging with timing
- **Type Safety** - Full type annotations for better development experience
- **Async Support** - High performance async operations
- **All HTTP Methods** - GET, POST, PUT, PATCH, DELETE support

## 💡 Key Features

### ✨ Simple & Intuitive
```python
from fasthttp import FastHTTP

app = FastHTTP()

@app.get(url="https://api.github.com/users/octocat")
async def get_user(resp):
    return resp.json()
```

### 🔍 Detailed Logging
```
16:09:18.955 │ INFO     │ fasthttp │ ✔ Sending 1 requests
16:09:19.519 │ INFO     │ fasthttp │ ✔ ← GET https://api.github.com [200] 458.26ms
```

### 🛡️ Type Safe
```python
from fasthttp.response import Response

@app.get(url="https://api.example.com")
async def handler(resp: Response) -> str:
    return resp.json()
```

## 🎯 Perfect For

- **API Testing** - Quick and easy API client development
- **Web Scraping** - Simple HTTP requests with logging
- **Microservices** - Lightweight HTTP client for service communication  
- **Prototyping** - Fast development with beautiful output

## 📖 Next Steps

Ready to get started? Jump to our [Quick Start Guide](quick-start.md) or explore the [API Reference](api-reference.md).

---

*FastHTTP Client - Making HTTP requests fast and beautiful* ⚡

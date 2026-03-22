<p align="center">
  <img src="https://fasthttp.readthedocs.io/ru/latest/logo.png" style="background:white; padding:12px; border-radius:10px; width:350">
</p>

<div align="center">

![httpx](https://img.shields.io/badge/httpx-0.28.1-blue.svg)
![ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)
![mypy](https://img.shields.io/badge/type%20checked-mypy-2E5090.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
[![CodSpeed](https://img.shields.io/endpoint?url=https://codspeed.io/badge.json)](https://codspeed.io/ndugram/fasthttp?utm_source=badge)

</div>

## Features

- **Simple API** - Minimal boilerplate with decorators
- **Beautiful Logging** - Colorful request/response logs with timing
- **Async Support** - Built on httpx for high performance
- **Type Safe** - Full type annotations with Pydantic support
- **All HTTP Methods** - GET, POST, PUT, PATCH, DELETE
- **Middleware** - Request/response interception and modification
- **Rate Limiting** - Multiple strategies (token bucket, leaky bucket, etc.)
- **HTTP/2 Support** - Optional HTTP/2 protocol support
- **Request Info** - Access to request details from response object

## Quick Start

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

### HTTP/2 Support

Enable HTTP/2 for better performance with servers that support it:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(http2=True)

@app.get(url="https://www.google.com/")
async def get_google(resp: Response):
    print(f"Status: {resp.status}")
    return resp.status

if __name__ == "__main__":
    app.run()
```

**Note:** Install with `pip install fasthttp-client[http2]` for HTTP/2 support. HTTP/2 works with servers like Google, GitHub, YouTube, and many others. Servers that don't support HTTP/2 will automatically fall back to HTTP/1.1.

### Rate Limiting

Control request rate with multiple strategies:

### Middleware

Add custom logic to requests and responses:

```python
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware
from fasthttp.response import Response
from fasthttp.routing import Route
from fasthttp.types import RequestsOptinal

class LoggingMiddleware(BaseMiddleware):
    async def before_request(
        self, route: Route, config: RequestsOptinal
    ) -> RequestsOptinal:
        print(f"Sending {route.method} to {route.url}")
        return config

app = FastHTTP(middleware=[LoggingMiddleware()])

@app.get(url="https://api.example.com/data")
async def get_data(resp: Response) -> dict:
    return resp.json()

if __name__ == "__main__":
    app.run()
```


## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## Security

See [SECURITY.md](SECURITY.md) for security policies.

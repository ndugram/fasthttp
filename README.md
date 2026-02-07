![image](./docs/logo-repo.png)

<div align="center">

![aiohttp](https://img.shields.io/badge/aiohttp-3.13.3-blue.svg)
![ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)
![mypy](https://img.shields.io/badge/type%20checked-mypy-2E5090.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Simple & Fast HTTP Client for Python**

[Documentation](docs/en/index.md) • [Quick Start](docs/en/quick-start.md) • [Examples](docs/en/examples.md)

</div>

## Features

- **Simple API** - Minimal boilerplate with decorators
- **Beautiful Logging** - Colorful request/response logs with timing
- **Async Support** - Built on aiohttp for high performance
- **Type Safe** - Full type annotations
- **All HTTP Methods** - GET, POST, PUT, PATCH, DELETE

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


##  Documentation

- **[Documentation](docs/index.md)** - Complete guide
- **[Quick Start](docs/quick-start.md)** - Get started in 2 minutes
- **[API Reference](docs/api-reference.md)** - Full API documentation
- **[Examples](docs/examples.md)** - Real-world examples
- **[Configuration](docs/configuration.md)** - Advanced settings


## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## Security

See [SECURITY.md](SECURITY.md) for security policies.

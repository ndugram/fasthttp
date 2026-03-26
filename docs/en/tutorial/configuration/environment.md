# Environment Variables

Configure FastHTTP using environment variables.

## Basic Usage

```python
import os
from fasthttp import FastHTTP

app = FastHTTP(
    debug=os.getenv("DEBUG", "false").lower() == "true",
    http2=os.getenv("HTTP2", "false").lower() == "true",
    get_request={
        "headers": {
            "Authorization": f"Bearer {os.getenv('API_TOKEN')}",
            "User-Agent": os.getenv("USER_AGENT", "MyApp/1.0"),
        },
        "timeout": float(os.getenv("TIMEOUT", "30.0")),
    },
)
```

## Example .env File

```bash
# .env
DEBUG=true
HTTP2=false
API_TOKEN=your-secret-token
USER_AGENT=MyApp/1.0
TIMEOUT=30.0
```

## Using python-dotenv

```python
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env file

app = FastHTTP(
    debug=os.getenv("DEBUG") == "true",
    get_request={
        "headers": {
            "Authorization": f"Bearer {os.getenv('API_TOKEN')}",
        }
    }
)
```

Install:

```bash
pip install python-dotenv
```

## Environment Variables Table

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable debug mode |
| `HTTP2` | `false` | Enable HTTP/2 |
| `API_TOKEN` | - | API authentication token |
| `USER_AGENT` | `fasthttp` | User-Agent header |
| `TIMEOUT` | `30.0` | Request timeout |
| `PROXY` | - | Proxy server URL |

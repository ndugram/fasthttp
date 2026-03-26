# Headers

Configure HTTP headers for requests.

## Global Headers

Apply headers to all requests:

```python
app = FastHTTP(
    get_request={
        "headers": {
            "Authorization": "Bearer your-token-here",
            "User-Agent": "MyApp/1.0",
            "Accept": "application/json",
        }
    }
)
```

## Local Headers

Apply headers to specific requests:

```python
@app.get(
    url="https://api.example.com/data",
    get_request={
        "headers": {"X-Custom-Header": "value"}
    }
)
async def handler(resp):
    return resp.json()
```

## Common Header Types

### Bearer Token

```python
app = FastHTTP(
    get_request={
        "headers": {"Authorization": "Bearer your-token-here"}
    }
)
```

### API Key

```python
app = FastHTTP(
    get_request={
        "headers": {"X-API-Key": "your-api-key"}
    }
)
```

### Basic Authentication

```python
import base64

app = FastHTTP(
    get_request={
        "headers": {
            "Authorization": f"Basic {base64.b64encode(b'username:password').decode()}"
        }
    }
)
```

## Dynamic Headers

For dynamic headers, use dependencies:

```python
from fasthttp import FastHTTP, Depends
import os


async def add_auth(route, config):
    token = os.getenv("API_TOKEN")
    config.setdefault("headers", {})["Authorization"] = f"Bearer {token}"
    return config


app = FastHTTP()


@app.get(
    url="https://api.example.com/data",
    dependencies=[Depends(add_auth)]
)
async def handler(resp):
    return resp.json()
```

## Headers Merge

Local headers merge with global headers:

```python
# Global
app = FastHTTP(
    get_request={
        "headers": {
            "User-Agent": "MyApp/1.0",
            "Accept": "application/json"
        }
    }
)

# Local - adds to global, doesn't replace
@app.get(
    url="https://api.example.com/data",
    get_request={
        "headers": {"X-Custom": "value"}
    }
)
async def handler(resp):
    # Result: User-Agent, Accept, X-Custom
    return resp.json()
```

# Lifespan

Lifespan allows running code before and after all requests.

## Basic Usage

```python
from contextlib import asynccontextmanager
from fasthttp import FastHTTP
from fasthttp.response import Response


@asynccontextmanager
async def lifespan(app: FastHTTP):
    # Startup - runs before requests
    print("Starting up...")
    app.auth_token = "my-secret-token"

    yield  # Requests execute here

    # Shutdown - runs after requests
    print("Shutting down...")


app = FastHTTP(lifespan=lifespan)


@app.get(url="https://api.example.com/data")
async def get_data(resp: Response) -> dict:
    return resp.json()


app.run()
```

Output:

```
Starting up...
INFO    | fasthttp    | FastHTTP started
INFO    | fasthttp    | Sending 1 requests
INFO    | fasthttp    | GET https://api.example.com/data 200 150ms
INFO    | fasthttp    | Done in 0.15s
Shutting down...
```

## Use Cases

### Loading Configuration

```python
import os
import json


@asynccontextmanager
async def lifespan(app: FastHTTP):
    # Load config from file
    with open("config.json") as f:
        app.config = json.load(f)
    
    yield
    
    # Cleanup if needed
    pass


app = FastHTTP(lifespan=lifespan)
```

### Connecting to Services

```python
import aioredis


@asynccontextmanager
async def lifespan(app: FastHTTP):
    # Connect to Redis
    app.redis = await aioredis.from_url("redis://localhost")
    print("Redis connected")

    yield

    # Close connection
    await app.redis.close()
    print("Redis disconnected")


app = FastHTTP(lifespan=lifespan)
```

### Loading Tokens

```python
import os


@asynccontextmanager
async def lifespan(app: FastHTTP):
    # Load token from environment
    app.api_token = os.getenv("API_TOKEN")
    
    yield
    
    # Token cleanup if needed


app = FastHTTP(lifespan=lifespan)
```

### Collecting Statistics

```python
@asynccontextmanager
async def lifespan(app: FastHTTP):
    # Initialize counters
    app.request_count = 0
    app.total_time = 0.0

    yield

    # Print statistics
    print(f"Total requests: {app.request_count}")
    print(f"Total time: {app.total_time:.2f}s")


app = FastHTTP(lifespan=lifespan)
```

## Without Lifespan

If `lifespan` is not specified, the application works normally:

```python
app = FastHTTP()  # No lifespan


@app.get(url="https://api.example.com/data")
async def get_data(resp: Response) -> dict:
    return resp.json()


app.run()
```

## Using App Attributes

You can add custom attributes to the app and access them in handlers:

```python
@asynccontextmanager
async def lifespan(app: FastHTTP):
    app.base_url = "https://api.example.com"
    app.api_key = "secret-key"
    yield


app = FastHTTP(lifespan=lifespan)


@app.get(url="https://api.example.com/data")
async def get_data(resp: Response) -> dict:
    # Access app attributes
    headers = {"X-API-Key": app.api_key}
    return resp.json()
```

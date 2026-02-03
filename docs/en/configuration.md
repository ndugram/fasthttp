# Configuration Guide

Advanced configuration options and customization for FastHTTP Client.

## 📚 Table of Contents

- [Basic Configuration](#basic-configuration)
- [Request-Specific Settings](#request-specific-settings)
- [Logging Configuration](#logging-configuration)
- [Timeout and Retry Settings](#timeout-and-retry-settings)
- [Headers and Authentication](#headers-and-authentication)
- [Environment Variables](#environment-variables)
- [Custom Configuration Patterns](#custom-configuration-patterns)

## 🔧 Basic Configuration

### Global Configuration
Configure defaults for all HTTP methods:

```python
from fasthttp import FastHTTP

app = FastHTTP(
    debug=False,  # Enable detailed logging
    get_request={
        "headers": {"User-Agent": "MyApp/1.0"},
        "timeout": 10,
    },
    post_request={
        "headers": {"Content-Type": "application/json"},
        "timeout": 30,
    },
)
```

### Method-Specific Configuration
Each HTTP method can have its own default configuration:

```python
app = FastHTTP(
    # Global defaults
    debug=True,
    
    # GET-specific defaults
    get_request={
        "headers": {
            "Accept": "application/json",
            "User-Agent": "FastHTTP-Client/1.0",
        },
        "timeout": 5,
        "allow_redirects": True,
    },
    
    # POST-specific defaults
    post_request={
        "headers": {
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        "timeout": 30,
        "allow_redirects": False,
    },
    
    # PUT-specific defaults
    put_request={
        "headers": {
            "Content-Type": "application/json",
        },
        "timeout": 30,
    },
    
    # PATCH-specific defaults
    patch_request={
        "headers": {
            "Content-Type": "application/json",
        },
        "timeout": 30,
    },
    
    # DELETE-specific defaults
    delete_request={
        "headers": {
            "Accept": "application/json",
        },
        "timeout": 10,
    },
)
```

## 📝 Request-Specific Settings

### Override Global Settings
Individual requests can override global configuration:

```python
# Uses global GET config + additional params
@app.get(url="https://api.example.com/data", params={"page": 1})
async def get_data(resp: Response):
    return resp.json()

# Override timeout for specific request
@app.get(url="https://slow-api.com/data", params={"timeout": 60})
async def get_slow_data(resp: Response):
    return resp.json()

# Custom headers for specific request
@app.post(
    url="https://api.example.com/upload",
    json={"file": "data"},
    data={"custom": "header"},  # This will be merged with global headers
)
async def upload_data(resp: Response):
    return resp.status
```

### Query Parameters
Add query parameters to any request:

```python
@app.get(
    url="https://api.example.com/search",
    params={
        "q": "fasthttp",
        "sort": "relevance",
        "page": 2,
        "per_page": 50,
    }
)
async def search(resp: Response):
    return resp.json()
```

## 📊 Logging Configuration

### Debug Mode
Enable detailed logging for development:

```python
# Basic debug mode
app = FastHTTP(debug=True)

# Debug with custom configuration
app = FastHTTP(debug=True)

# Logging will show:
# - Request headers
# - Response headers
# - Response body (truncated)
# - Handler results
# - Timing information
```

### Log Levels and Output

#### Info Level (Default)
```
16:09:18.955 │ INFO     │ fasthttp │ ✔ FastHTTP started
16:09:19.520 │ INFO     │ fasthttp │ ✔ ✔️ GET     https://api.example.com  200 458.26ms
```

#### Debug Level
```
16:09:18.954 │ DEBUG    │ fasthttp │ 🐛 Registered route: GET https://api.example.com
16:09:19.519 │ DEBUG    │ fasthttp │ 🐛 → GET https://api.example.com | headers={...}
16:09:19.520 │ DEBUG    │ fasthttp │ ↳ {"data": "response content"}
```

### Custom Logging
For advanced logging scenarios, you might want to capture logs programmatically:

```python
import logging
from fasthttp import FastHTTP

# Capture logs
log_capture = []

class LogCapture(logging.Handler):
    def emit(self, record):
        log_capture.append(self.format(record))

# Add custom handler
app = FastHTTP(debug=True)
logger = logging.getLogger("fasthttp")
logger.addHandler(LogCapture())

# Run requests
app.run()

# Process captured logs
for log_entry in log_capture:
    print(f"CAPTURED: {log_entry}")
```

## ⏱️ Timeout and Retry Settings

### Request Timeout
Set timeout for individual requests or globally:

```python
# Global timeout
app = FastHTTP(get_request={"timeout": 30})

# Per-request timeout
@app.get(url="https://fast-api.com/data", timeout=5)
async def fast_request(resp: Response):
    return resp.status

@app.get(url="https://slow-api.com/data", timeout=120)
async def slow_request(resp: Response):
    return resp.status
```

### Timeout Configuration Options

```python
# Different timeout types
timeout_config = {
    "timeout": 30,  # Total request timeout in seconds
    
    # aiohttp specific timeout configuration
    "timeout": aiohttp.ClientTimeout(
        total=30,      # Total timeout
        connect=10,     # Connection timeout
        sock_read=10,  # Socket read timeout
    )
}
```

## 🔐 Headers and Authentication

### Common Authentication Patterns

#### Bearer Token
```python
app = FastHTTP(
    get_request={
        "headers": {
            "Authorization": "Bearer YOUR_JWT_TOKEN",
        },
    },
)
```

#### API Key
```python
app = FastHTTP(
    get_request={
        "headers": {
            "X-API-Key": "your-api-key",
        },
    },
)
```

#### Basic Authentication
```python
import base64

# Encode credentials
credentials = base64.b64encode(b"username:password").decode()

app = FastHTTP(
    get_request={
        "headers": {
            "Authorization": f"Basic {credentials}",
        },
    },
)
```

#### Custom Header Patterns
```python
app = FastHTTP(
    get_request={
        "headers": {
            # User agent
            "User-Agent": "FastHTTP-Client/1.0",
            
            # Content types
            "Content-Type": "application/json",
            "Accept": "application/json",
            
            # Custom headers
            "X-Client-Version": "1.0.0",
            "X-Request-ID": "req-12345",
            
            # Cache control
            "Cache-Control": "no-cache",
            
            # CORS
            "Origin": "https://yourapp.com",
        },
    },
)
```

### Dynamic Headers
For headers that change per request:

```python
import uuid
from datetime import datetime

def generate_headers():
    return {
        "X-Request-ID": str(uuid.uuid4()),
        "X-Timestamp": datetime.utcnow().isoformat(),
        "User-Agent": f"FastHTTP-Client/1.0-{uuid.uuid4().hex[:8]}",
    }

@app.get(url="https://api.example.com/data")
async def dynamic_headers_request(resp: Response):
    # Headers will be merged with global config
    return resp.status
```

## 🌐 Environment Variables

### Configuration with Environment Variables
Use environment variables for sensitive and environment-specific configuration:

```python
import os
from fasthttp import FastHTTP

# Read from environment
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.example.com")
API_KEY = os.getenv("API_KEY")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
TIMEOUT = int(os.getenv("TIMEOUT", "30"))

# Configure app with environment variables
app = FastHTTP(
    debug=DEBUG,
    get_request={
        "headers": {
            "Authorization": f"Bearer {API_KEY}",
            "User-Agent": os.getenv("USER_AGENT", "FastHTTP-Client/1.0"),
        },
        "timeout": TIMEOUT,
    },
)
```

### Environment-Specific Configuration
Different settings for different environments:

```python
import os

ENV = os.getenv("ENVIRONMENT", "development")

if ENV == "production":
    app = FastHTTP(
        debug=False,
        get_request={
            "headers": {
                "User-Agent": "Production-App/1.0",
            },
            "timeout": 30,
        },
    )
elif ENV == "staging":
    app = FastHTTP(
        debug=True,
        get_request={
            "headers": {
                "User-Agent": "Staging-App/1.0",
            },
            "timeout": 60,
        },
    )
else:  # development
    app = FastHTTP(
        debug=True,
        get_request={
            "headers": {
                "User-Agent": "Dev-App/1.0",
            },
            "timeout": 10,
        },
    )
```

## 🎛️ Custom Configuration Patterns

### Configuration Classes
Organize configuration in classes:

```python
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class APIConfig:
    base_url: str
    api_key: str
    timeout: int = 30
    debug: bool = False
    headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {}
    
    def get_fasthttp_config(self, method: str) -> Dict[str, Any]:
        base_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "FastHTTP-Client/1.0",
        }
        base_headers.update(self.headers)
        
        return {
            "debug": self.debug,
            f"{method.lower()}_request": {
                "headers": base_headers,
                "timeout": self.timeout,
            },
        }

# Usage
github_config = APIConfig(
    base_url="https://api.github.com",
    api_key=os.getenv("GITHUB_TOKEN"),
    timeout=10,
    debug=True,
    headers={
        "Accept": "application/vnd.github.v3+json",
    },
)

app = FastHTTP(**github_config.get_fasthttp_config("GET"))
```

### Configuration Factory
Create configuration factories for different APIs:

```python
class APIConfigFactory:
    @staticmethod
    def github(token: str, debug: bool = False):
        return FastHTTP(
            debug=debug,
            get_request={
                "headers": {
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "FastHTTP-GitHub/1.0",
                },
                "timeout": 10,
            },
        )
    
    @staticmethod
    def weather(api_key: str, debug: bool = False):
        return FastHTTP(
            debug=debug,
            get_request={
                "headers": {
                    "X-RapidAPI-Key": api_key,
                    "X-RapidAPI-Host": "weather-api.p.rapidapi.com",
                },
                "timeout": 15,
            },
        )
    
    @staticmethod
    def jsonplaceholder(debug: bool = False):
        return FastHTTP(
            debug=debug,
            get_request={
                "headers": {
                    "User-Agent": "FastHTTP-JSONPlaceholder/1.0",
                },
                "timeout": 10,
            },
        )

# Usage
github_client = APIConfigFactory.github(os.getenv("GITHUB_TOKEN"), debug=True)
weather_client = APIConfigFactory.weather(os.getenv("WEATHER_API_KEY"))
json_client = APIConfigFactory.jsonplaceholder()
```

### Configuration Validation
Validate configuration before use:

```python
from typing import Optional
import os

class ValidatedConfig:
    def __init__(self):
        self.api_key = self._validate_api_key()
        self.base_url = self._validate_base_url()
        self.timeout = self._validate_timeout()
        self.debug = self._validate_debug()
    
    def _validate_api_key(self) -> str:
        key = os.getenv("API_KEY")
        if not key:
            raise ValueError("API_KEY environment variable is required")
        return key
    
    def _validate_base_url(self) -> str:
        url = os.getenv("API_BASE_URL")
        if not url:
            raise ValueError("API_BASE_URL environment variable is required")
        if not url.startswith(("http://", "https://")):
            raise ValueError("API_BASE_URL must start with http:// or https://")
        return url
    
    def _validate_timeout(self) -> int:
        timeout = os.getenv("TIMEOUT", "30")
        try:
            timeout_int = int(timeout)
            if timeout_int <= 0:
                raise ValueError("TIMEOUT must be positive")
            return timeout_int
        except ValueError:
            raise ValueError("TIMEOUT must be a valid integer")
    
    def _validate_debug(self) -> bool:
        debug = os.getenv("DEBUG", "false")
        return debug.lower() in ("true", "1", "yes")

# Usage
try:
    config = ValidatedConfig()
    app = FastHTTP(
        debug=config.debug,
        get_request={
            "headers": {"Authorization": f"Bearer {config.api_key}"},
            "timeout": config.timeout,
        },
    )
except ValueError as e:
    print(f"Configuration error: {e}")
    exit(1)
```

## 🔧 Advanced Configuration Examples

### Multi-Environment Setup
```python
import os
from enum import Enum

class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging" 
    PRODUCTION = "production"

def create_app_for_environment(env: Environment) -> FastHTTP:
    configs = {
        Environment.DEVELOPMENT: {
            "debug": True,
            "timeout": 30,
            "headers": {"User-Agent": "Dev-Client/1.0"},
        },
        Environment.STAGING: {
            "debug": True,
            "timeout": 60,
            "headers": {"User-Agent": "Staging-Client/1.0"},
        },
        Environment.PRODUCTION: {
            "debug": False,
            "timeout": 10,
            "headers": {"User-Agent": "Prod-Client/1.0"},
        },
    }
    
    config = configs[env]
    return FastHTTP(
        debug=config["debug"],
        get_request={
            "headers": config["headers"],
            "timeout": config["timeout"],
        },
    )

# Usage
env = Environment(os.getenv("ENVIRONMENT", "development"))
app = create_app_for_environment(env)
```

### Plugin-Style Configuration
```python
class HTTPClientPlugin:
    def __init__(self, name: str):
        self.name = name
        self.headers = {}
        self.timeout = 30
    
    def add_header(self, key: str, value: str):
        self.headers[key] = value
    
    def set_timeout(self, timeout: int):
        self.timeout = timeout
    
    def configure_app(self, app: FastHTTP):
        method = self.name.upper()
        config = {
            "headers": self.headers.copy(),
            "timeout": self.timeout,
        }
        
        setattr(app, f"{method.lower()}_request", config)

# Usage
auth_plugin = HTTPClientPlugin("get")
auth_plugin.add_header("Authorization", "Bearer token")
auth_plugin.set_timeout(15)

app = FastHTTP()
auth_plugin.configure_app(app)
```

---

*Proper configuration is key to building robust HTTP clients! 🚀*

*For more information, see the [API Reference](api-reference.md) and [Examples](examples.md)* 📚

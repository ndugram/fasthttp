# Examples

Real-world examples and use cases for FastHTTP Client.

## 📚 Table of Contents

- [GitHub API Integration](#github-api-integration)
- [JSONPlaceholder Examples](#jsonplaceholder-examples)
- [HTTPBin Testing](#httpbin-testing)
- [File Upload](#file-upload)
- [Authentication Examples](#authentication-examples)
- [Error Handling](#error-handling)
- [Performance Testing](#performance-testing)

## 🐙 GitHub API Integration

### Get User Information
```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(
    get_request={
        "headers": {
            "Authorization": "Bearer YOUR_GITHUB_TOKEN",
            "User-Agent": "FastHTTP-GitHub-App",
        },
        "timeout": 10,
    },
)

@app.get(url="https://api.github.com/user")
async def get_current_user(resp: Response):
    user_data = resp.json()
    return f"""
👤 User: {user_data['name']} (@{user_data['login']})
📧 Email: {user_data['email']}
🏢 Company: {user_data.get('company', 'N/A')}
📍 Location: {user_data.get('location', 'N/A')}
📊 Public Repos: {user_data['public_repos']}
⭐ Followers: {user_data['followers']}
👥 Following: {user_data['following']}
"""

@app.get(url="https://api.github.com/repos/microsoft/vscode")
async def get_vscode_stats(resp: Response):
    repo = resp.json()
    return f"""
📦 Repository: {repo['full_name']}
⭐ Stars: {repo['stargazers_count']}
🍴 Forks: {repo['forks_count']}
🐛 Issues: {repo['open_issues_count']}
📝 Language: {repo['language']}
📅 Updated: {repo['updated_at']}
"""

@app.get(url="https://api.github.com/users/octocat")
async def get_octocat_profile(resp: Response):
    user = resp.json()
    return f"🐙 Octocat: {user['name']} - {user['bio']}"

if __name__ == "__main__":
    app.run()
```

### Repository Search
```python
app = FastHTTP(
    get_request={
        "headers": {
            "Authorization": "Bearer YOUR_TOKEN",
            "Accept": "application/vnd.github.v3+json",
        },
    },
)

@app.get(url="https://api.github.com/search/repositories")
async def search_python_repos(resp: Response):
    data = resp.json()
    repos = data['items'][:5]  # Top 5 results
    
    result = "🔍 Top Python Repositories:\n\n"
    for i, repo in enumerate(repos, 1):
        result += f"{i}. {repo['full_name']} ⭐ {repo['stargazers_count']}\n"
        result += f"   📝 {repo['description'] or 'No description'}\n\n"
    
    return result

if __name__ == "__main__":
    app.run()
```

## 📝 JSONPlaceholder Examples

### Blog Post Management
```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()

# Get all posts
@app.get(url="https://jsonplaceholder.typicode.com/posts")
async def get_all_posts(resp: Response):
    posts = resp.json()
    return f"📚 Found {len(posts)} posts"

# Get specific post
@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def get_post(resp: Response):
    post = resp.json()
    return f"""
📖 Post #{post['id']}: {post['title']}
👤 User ID: {post['userId']}
📄 Body: {post['body'][:100]}...
"""

# Create new post
@app.post(url="https://jsonplaceholder.typicode.com/posts", json={
    "title": "FastHTTP Client",
    "body": "This is an awesome HTTP client!",
    "userId": 1
})
async def create_post(resp: Response):
    new_post = resp.json()
    return f"✅ Created post #{new_post['id']}: {new_post['title']}"

# Update post
@app.put(url="https://jsonplaceholder.typicode.com/posts/1", json={
    "id": 1,
    "title": "Updated with FastHTTP",
    "body": "Updated content",
    "userId": 1
})
async def update_post(resp: Response):
    updated = resp.json()
    return f"🔄 Updated post #{updated['id']}"

# Delete post
@app.delete(url="https://jsonplaceholder.typicode.com/posts/1")
async def delete_post(resp: Response):
    return f"🗑️ Delete status: {resp.status}"

if __name__ == "__main__":
    app.run()
```

## 🌐 HTTPBin Testing

### Request Testing
```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(
    get_request={
        "headers": {
            "User-Agent": "FastHTTP-Tester/1.0",
            "X-Custom-Header": "test-value",
        },
    },
)

@app.get(url="https://httpbin.org/get")
async def test_get(resp: Response):
    data = resp.json()
    return f"""
🌐 GET Test Results:
📡 URL: {data['url']}
🖥️ Origin: {data['origin']}
📋 Headers: {len(data['headers'])} headers received
"""

@app.post(url="https://httpbin.org/post", json={
    "name": "FastHTTP",
    "version": "1.0",
    "features": ["async", "logging", "simple"]
})
async def test_post_json(resp: Response):
    data = resp.json()
    return f"""
📤 POST JSON Test:
📝 Sent: {data['json']}
✅ Content-Type: {data['headers']['Content-Type']}
"""

@app.post(url="https://httpbin.org/post", data={
    "username": "testuser",
    "password": "secret123"
})
async def test_post_form(resp: Response):
    data = resp.json()
    return f"""
📋 POST Form Test:
🔑 Form data: {data['form']}
"""

@app.get(url="https://httpbin.org/status/418")
async def test_status_code(resp: Response):
    return f"☕ Status {resp.status}: I'm a teapot!"

@app.get(url="https://httpbin.org/delay/2")
async def test_delay(resp: Response):
    return f"⏰ Delayed response received after 2 seconds"

if __name__ == "__main__":
    app.run()
```

## 📁 File Upload Simulation

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()

@app.post(url="https://httpbin.org/post", data={
    "file": "fake_file_content",
    "description": "Test file upload"
})
async def simulate_file_upload(resp: Response):
    data = resp.json()
    return f"""
📤 File Upload Simulation:
📁 Files: {data.get('files', {})}
📝 Form: {data.get('form', {})}
"""

if __name__ == "__main__":
    app.run()
```

## 🔐 Authentication Examples

### Bearer Token Authentication
```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(
    get_request={
        "headers": {
            "Authorization": "Bearer YOUR_JWT_TOKEN",
        },
    },
)

@app.get(url="https://api.example.com/profile")
async def get_protected_profile(resp: Response):
    if resp.status == 200:
        user = resp.json()
        return f"👤 Welcome, {user['name']}!"
    elif resp.status == 401:
        return "❌ Unauthorized - Invalid token"
    else:
        return f"❓ Status {resp.status}"

@app.get(url="https://api.example.com/admin/dashboard")
async def get_admin_data(resp: Response):
    if resp.status == 403:
        return "🚫 Access denied - Admin privileges required"
    elif resp.status == 200:
        return "✅ Admin access granted"
    else:
        return f"❓ Status {resp.status}"
```

### API Key Authentication
```python
app = FastHTTP(
    get_request={
        "headers": {
            "X-API-Key": "your-api-key-here",
        },
    },
)

@app.get(url="https://api.weather.com/v1/current")
async def get_weather(resp: Response):
    weather = resp.json()
    return f"""
🌤️ Weather Data:
📍 Location: {weather['location']}
🌡️ Temperature: {weather['temperature']}°C
💨 Condition: {weather['condition']}
"""
```

## ⚠️ Error Handling

### Robust Error Handling
```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)

@app.get(url="https://httpbin.org/status/404")
async def handle_404(resp: Response):
    if resp.status == 404:
        return "🔍 Resource not found"
    return f"Status: {resp.status}"

@app.get(url="https://httpbin.org/status/500")
async def handle_500(resp: Response):
    if resp.status >= 500:
        return "🔥 Server error occurred"
    return f"Status: {resp.status}"

@app.get(url="https://httpbin.org/delay/10")
async def handle_timeout(resp: Response):
    if resp is None:
        return "⏰ Request timed out"
    return f"✅ Received response: {resp.status}"

if __name__ == "__main__":
    try:
        app.run()
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
```

## ⚡ Performance Testing

### Concurrent Request Testing
```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()

# Multiple endpoints for performance testing
endpoints = [
    "https://httpbin.org/get",
    "https://jsonplaceholder.typicode.com/posts/1", 
    "https://reqres.in/api/users/1",
]

for i, endpoint in enumerate(endpoints):
    @app.get(url=endpoint)
    async def test_endpoint(resp: Response, endpoint=endpoint):
        return f"✅ {endpoint}: {resp.status} ({len(resp.text)} chars)"

if __name__ == "__main__":
    print("🚀 Starting performance test...")
    app.run()
```

### Load Testing Simulation
```python
app = FastHTTP()

# Simulate multiple API calls
for i in range(5):
    @app.get(url=f"https://httpbin.org/get?id={i}")
    async def load_test(resp: Response, i=i):
        data = resp.json()
        return f"Request {i}: ✅ {data['args']}"

if __name__ == "__main__":
    app.run()
```

## 🔄 Real-World API Examples

### REST API Client
```python
from fasthttp import FastHTTP
from fasthttp.response import Response

class APIClient:
    def __init__(self, base_url: str, api_key: str):
        self.app = FastHTTP(
            get_request={
                "headers": {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
            },
        )
        self.base_url = base_url
    
    def get_users(self):
        @self.app.get(url=f"{self.base_url}/users")
        async def handler(resp: Response):
            return resp.json()
        return self.app
    
    def create_user(self, user_data: dict):
        @self.app.post(url=f"{self.base_url}/users", json=user_data)
        async def handler(resp: Response):
            return resp.json()
        return self.app
    
    def run(self):
        self.app.run()

# Usage
client = APIClient("https://api.example.com", "your-api-key")
client.get_users()
client.create_user({"name": "John", "email": "john@example.com"})
client.run()
```

### Weather API Client
```python
app = FastHTTP(
    get_request={
        "headers": {
            "X-RapidAPI-Key": "your-rapidapi-key",
        },
    },
)

@app.get(url="https://weather-api.p.rapidapi.com/current")
async def get_weather(resp: Response):
    if resp.status == 200:
        weather = resp.json()
        return f"""
🌤️ Current Weather:
📍 Location: {weather['location']['name']}
🌡️ Temperature: {weather['current']['temp_c']}°C
💨 Wind: {weather['current']['wind_kph']} km/h
☁️ Condition: {weather['current']['condition']['text']}
"""
    return f"❌ Weather API error: {resp.status}"

if __name__ == "__main__":
    app.run()
```

## 🎯 Best Practices

### 1. Environment Configuration
```python
import os
from fasthttp import FastHTTP

# Use environment variables for sensitive data
api_key = os.getenv("API_KEY", "default-key")
base_url = os.getenv("API_BASE_URL", "https://api.example.com")

app = FastHTTP(
    get_request={
        "headers": {
            "Authorization": f"Bearer {api_key}",
        },
    },
)
```

### 2. Response Validation
```python
@app.get(url="https://api.example.com/data")
async def validated_response(resp: Response):
    if resp.status != 200:
        return f"❌ Error: {resp.status}"
    
    try:
        data = resp.json()
        if not isinstance(data, list):
            return "❌ Expected list response"
        return f"✅ Received {len(data)} items"
    except Exception:
        return "❌ Invalid JSON response"
```

### 3. Reusable Configuration
```python
class BaseAPIClient:
    def __init__(self, base_url: str, headers: dict):
        self.app = FastHTTP(get_request={"headers": headers})
        self.base_url = base_url
    
    def add_endpoint(self, method: str, path: str, **kwargs):
        url = f"{self.base_url}{path}"
        
        if method.upper() == "GET":
            return self.app.get(url=url, **kwargs)
        elif method.upper() == "POST":
            return self.app.post(url=url, **kwargs)
        # ... other methods

# Usage
client = BaseAPIClient("https://api.github.com", {
    "Authorization": "token YOUR_TOKEN",
    "User-Agent": "FastHTTP-App",
})

client.add_endpoint("GET", "/user")
client.add_endpoint("GET", "/repos", params={"sort": "updated"})
```

---

*These examples demonstrate the flexibility and power of FastHTTP Client! 🚀*

*For more advanced usage, check out the [API Reference](api-reference.md)* 📚

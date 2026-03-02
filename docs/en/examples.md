# Examples

Practical examples for common use cases.

## Basic GET

```python
from fasthttp import FastHTTP

app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def get_post(resp):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

## POST JSON

Send JSON data to create resource:

```python
@app.post(url="https://jsonplaceholder.typicode.com/posts", json={
    "title": "FastHTTP",
    "body": "Content here",
    "userId": 1
})
async def create_post(resp):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

## Query Parameters

Pass query string parameters:

```python
@app.get(url="https://jsonplaceholder.typicode.com/posts", params={
    "userId": 1,
    "_limit": 5
})
async def get_user_posts(resp):
    posts = resp.json()
    return f"Found {len(posts)} posts"


if __name__ == "__main__":
    app.run()
```

## Headers

Set custom headers globally:

```python
app = FastHTTP(
    get_request={
        "headers": {
            "Authorization": "Bearer YOUR_TOKEN",
            "User-Agent": "MyApp/1.0",
        },
    },
)


@app.get(url="https://api.example.com/protected")
async def get_protected(resp):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

## Error Handling

Errors are logged automatically. Use debug mode to see details:

```python
app = FastHTTP(debug=True)


@app.get(url="https://httpbin.org/status/404")
async def handle_404(resp):
    return f"Status: {resp.status}"


@app.get(url="https://httpbin.org/status/500")
async def handle_500(resp):
    return f"Error: {resp.status}"


if __name__ == "__main__":
    app.run()
```

## Concurrent Requests

All registered requests run in parallel:

```python
app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def get_post(resp):
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/users/1")
async def get_user(resp):
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/comments/1")
async def get_comment(resp):
    return resp.json()


if __name__ == "__main__":
    app.run()
    # All three requests run concurrently
```

## Multiple Methods

Use all HTTP methods:

```python
app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def get_post(resp):
    return resp.json()


@app.post(url="https://jsonplaceholder.typicode.com/posts", json={
    "title": "New Post",
    "body": "Content",
    "userId": 1
})
async def create_post(resp):
    return resp.status


@app.put(url="https://jsonplaceholder.typicode.com/posts/1", json={
    "id": 1,
    "title": "Updated",
    "body": "New content",
    "userId": 1
})
async def update_post(resp):
    return resp.status


@app.patch(url="https://jsonplaceholder.typicode.com/posts/1", json={
    "title": "Patched"
})
async def patch_post(resp):
    return resp.status


@app.delete(url="https://jsonplaceholder.typicode.com/posts/1")
async def delete_post(resp):
    return resp.status


if __name__ == "__main__":
    app.run()
```

## Pydantic Validation

Validate responses with Pydantic models:

```python
from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    email: str


class Post(BaseModel):
    id: int
    title: str
    body: str
    userId: int


app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/users/1", response_model=User)
async def get_user(resp):
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1", response_model=Post)
async def get_post(resp):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

## HTTP/2

Enable HTTP/2 for better performance:

```bash
pip install fasthttp-client[http2]
```

```python
app = FastHTTP(http2=True)


@app.get(url="https://example.com/")
async def get_example(resp):
    return resp.status


if __name__ == "__main__":
    app.run()
```

## Full Example

Complete application with multiple endpoints:

```python
from fasthttp import FastHTTP

app = FastHTTP(
    debug=True,
    get_request={
        "headers": {"User-Agent": "MyApp/1.0"},
    },
)


@app.get(url="https://jsonplaceholder.typicode.com/users")
async def get_all_users(resp):
    users = resp.json()
    return f"Found {len(users)} users"


@app.get(url="https://jsonplaceholder.typicode.com/users/1")
async def get_user(resp):
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/posts", params={"userId": 1})
async def get_user_posts(resp):
    return resp.json()


if __name__ == "__main__":
    app.run()
```

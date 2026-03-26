# First Steps

Get started with FastHTTP in less than 2 minutes.

## Installation

Install FastHTTP with pip:

```bash
pip install fasthttp-client
```

For HTTP/2 support:

```bash
pip install fasthttp-client[http2]
```

## Your First Request

Create a file `example.py`:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def main(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()
```

Run it:

```bash
python example.py
```

Output:

```
INFO    | fasthttp    | FastHTTP started
INFO    | fasthttp    | Sending 1 requests
INFO    | fasthttp    | GET https://jsonplaceholder.typicode.com/posts/1 200 234.56ms
INFO    | fasthttp    | Done in 0.24s
```

## Important Requirement

Handler functions must have a return type annotation:

```python
async def handler(resp: Response) -> dict:  # Required!
    return resp.json()
```

Without the `-> dict` annotation, the function will not work.

## How It Works

When you call `app.run()`, FastHTTP:

1. Collects all registered routes (functions with `@app.get`, `@app.post`, etc.)
2. Validates each handler has type annotations
3. Creates async tasks for all requests
4. Executes requests in parallel using asyncio
5. For each request:
   - Applies dependencies
   - Runs middleware.before_request()
   - Checks security (SSRF, etc.)
   - Sends HTTP request via httpx
   - Runs middleware.after_response()
   - Calls your handler function with Response
6. Logs results and finishes

## Key Concepts

- **Route**: Function decorated with `@app.get()`, `@app.post()`, etc.
- **Handler**: Function that processes the response
- **Response**: Object containing server's response (status, body, headers)
- **Dependency**: Function that modifies request config before sending
- **Middleware**: Plugin that can modify requests and responses globally

## Next Steps

Continue learning:

- [HTTP Methods](http-methods.md) - All supported HTTP methods
- [Request Parameters](request-parameters.md) - Query, JSON, headers
- [Configuration](../en/configuration.md) - More settings

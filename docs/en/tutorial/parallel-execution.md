# Parallel Execution

FastHTTP automatically executes all registered requests in parallel.

## How It Works

When you call `app.run()`, FastHTTP:

1. Collects all registered routes
2. Creates an async task for each route
3. Executes all tasks concurrently using `asyncio.gather()`
4. Waits for all requests to complete
5. Logs the results

## Example

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def get_post(resp: Response) -> dict:
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/users/1")
async def get_user(resp: Response) -> dict:
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/comments/1")
async def get_comment(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    # All three requests execute in parallel
    app.run()
```

## Performance Comparison

### Sequential Execution

```
Request 1: 150ms
Request 2: 120ms  (starts after request 1)
Request 3: 110ms  (starts after request 2)
Total: ~380ms
```

### Parallel Execution (FastHTTP)

```
Request 1: 150ms
Request 2: 120ms
Request 3: 110ms
Total: ~150ms (longest request)
```

Output:

```
INFO    | fasthttp    | FastHTTP started
INFO    | fasthttp    | Sending 3 requests
INFO    | fasthttp    | GET https://jsonplaceholder.typicode.com/posts/1 200 150ms
INFO    | fasthttp    | GET https://jsonplaceholder.typicode.com/users/1 200 120ms
INFO    | fasthttp    | GET https://jsonplaceholder.typicode.com/comments/1 200 110ms
INFO    | fasthttp    | Done in 0.15s
```

## Single Request

If you have only one request, it executes normally:

```python
app = FastHTTP()


@app.get(url="https://api.example.com/data")
async def single_request(resp: Response) -> dict:
    return resp.json()


app.run()
```

## When Parallelism Matters

Parallel execution is especially beneficial when:

- Making multiple API calls
- Fetching data from multiple services
- Processing multiple resources

The more requests you have, the more time you save.

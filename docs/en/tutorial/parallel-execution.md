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

## Limiting Concurrency

By default, all routes run fully in parallel. Use `concurrency` to cap how many requests execute at the same time.

```python
app = FastHTTP(concurrency=5)
```

This is useful when:

- The target API has a rate limit (e.g. 5 req/s)
- You want to avoid overwhelming a server with 100+ simultaneous connections
- You need predictable resource usage

### Example

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

# At most 3 requests run at the same time
app = FastHTTP(concurrency=3)


@app.get(url="https://api.example.com/items/1")
async def item_1(resp: Response) -> dict:
    return resp.json()


@app.get(url="https://api.example.com/items/2")
async def item_2(resp: Response) -> dict:
    return resp.json()


@app.get(url="https://api.example.com/items/3")
async def item_3(resp: Response) -> dict:
    return resp.json()


@app.get(url="https://api.example.com/items/4")
async def item_4(resp: Response) -> dict:
    return resp.json()


@app.get(url="https://api.example.com/items/5")
async def item_5(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    # First 3 start immediately, remaining 2 wait for a slot
    app.run()
```

`None` (default) means no limit — all routes run in parallel.

## When Parallelism Matters

Parallel execution is especially beneficial when:

- Making multiple API calls
- Fetching data from multiple services
- Processing multiple resources

The more requests you have, the more time you save.

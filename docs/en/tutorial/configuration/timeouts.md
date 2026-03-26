# Timeouts

Configure request timeouts.

## Global Timeout

```python
app = FastHTTP(
    get_request={"timeout": 30.0}
)
```

## Per-Request Timeout

```python
@app.get(url="https://api.example.com/fast", timeout=5.0)
async def fast_request(resp):
    return resp.json()


@app.get(url="https://api.example.com/slow", timeout=120.0)
async def slow_request(resp):
    return resp.json()
```

## Different Timeouts by Method

```python
app = FastHTTP(
    get_request={"timeout": 30.0},
    post_request={"timeout": 60.0},
    put_request={"timeout": 60.0},
    delete_request={"timeout": 30.0},
)
```

## Recommendations

| Request Type | Timeout |
|--------------|---------|
| GET requests | 10-30 seconds |
| POST/PUT requests | 30-60 seconds |
| File uploads | 120+ seconds |
| Quick checks | 5-10 seconds |

## Built-in Timeouts

FastHTTP has built-in timeouts:

- Connection timeout: 10 seconds
- Request timeout: 30 seconds (default)

These prevent application hanging during network issues.

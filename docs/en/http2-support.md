# HTTP/2

Enable HTTP/2 for better performance.

## Install

```bash
pip install fasthttp-client[http2]
```

## Enable

```python
app = FastHTTP(http2=True)
```

## Features

- Multiplexing — multiple requests on single connection
- Header compression (HPACK)
- Lower latency

## Requirements

- HTTPS required
- Server must support HTTP/2

## Check

```python
print(app._http2)  # True or False
```

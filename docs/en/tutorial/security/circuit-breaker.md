# Circuit Breaker

Automatic protection against failing hosts.

## How It Works

If a host stops responding (multiple timeouts or errors), FastHTTP automatically stops sending requests to that host temporarily.

## What It Protects Against

- Flooding a failed service with requests
- Wasting resources on non-working hosts
- Cascading failures

## Behavior

1. Host experiences multiple failures
2. Circuit breaker opens
3. Requests to that host are blocked
4. After waiting period, FastHTTP checks if host recovered
5. If recovered, normal operation resumes

## Configuration

Circuit breaker is enabled by default. You can disable it:

```python
app = FastHTTP(security=False)
```

## Logging

When circuit breaker activates:

```
ERROR | Circuit breaker open for: api.example.com
```

## Best Practices

- Keep security enabled
- Monitor logs for circuit breaker events
- Implement proper error handling in handlers

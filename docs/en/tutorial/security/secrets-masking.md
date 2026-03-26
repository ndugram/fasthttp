# Secrets Masking

Automatic hiding of sensitive data in logs.

## How It Works

When debug mode is enabled, FastHTTP automatically masks sensitive data:

### Headers Masked

- `Authorization`
- `Cookie`
- `X-API-Key`

### URL Parameters Masked

- `api_key`
- `token`
- `password`

## Example

Instead of:

```
Authorization: Bearer sk-1234567890abcdef
```

Logs show:

```
Authorization: *****
```

## Enabling Debug Mode

```python
app = FastHTTP(debug=True)
```

## Disabling

You can disable security entirely:

```python
app = FastHTTP(security=False)
```

Not recommended for production.

## Best Practices

1. Keep security enabled
2. Use environment variables for secrets
3. Monitor logs for blocked requests
4. Review what gets logged

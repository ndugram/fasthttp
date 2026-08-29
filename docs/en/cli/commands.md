# CLI Commands

Available CLI commands.

## HTTP Methods

### GET

```bash
fasthttp get https://api.example.com/data
```

With query parameters:

```bash
fasthttp get "https://api.example.com/search?q=test&page=1"
```

### POST

```bash
fasthttp post https://api.example.com/users --json '{"name": "John"}'
```

### PUT

```bash
fasthttp put https://api.example.com/users/1 --json '{"name": "Jane"}'
```

### PATCH

```bash
fasthttp patch https://api.example.com/users/1 --json '{"age": 25}'
```

### DELETE

```bash
fasthttp delete https://api.example.com/users/1
```

## Code Generation

### codegen

Generate a fasthttp client from an OpenAPI 3.x spec (local file, or URL — JSON or YAML):

```bash
fasthttp codegen openapi.json -o client.py
fasthttp codegen https://api.example.com/openapi.json -o client.py
```

Endpoints with no path parameters become idiomatic `@app.get`/`@app.post` routes.
fasthttp has no dynamic path-parameter routing (a route's URL is fixed at
decoration time), so endpoints *with* path parameters (`/users/{id}`) are
generated as plain `AsyncSession`-based functions instead:

```python
@app.get(url="/pets", tags=["pets"], response_model=PetList)
async def list_pets(resp: Response) -> dict:
    return resp.json()

async def get_pet(session: AsyncSession, petId: str) -> dict | None:
    resp = await session.get(f"{base_url}/pets/{petId}")
    return resp.json() if resp else None
```

Pydantic models are generated from `components.schemas` — `$ref` is resolved
and string enums become `Literal[...]`.

!!! note "MVP limitations"
    `oneOf`/`anyOf`/`allOf` schema composition falls back to `Any`, and
    inline (unnamed) nested objects fall back to `dict[str, Any]` instead of
    a generated nested model. YAML specs require `pip install fasthttp-client[codegen]`
    (or `pip install pyyaml` directly) — JSON specs need nothing extra.

## Output Format

Second argument determines output:

| Format | Description |
|--------|-------------|
| `status` | Status code only (default) |
| `json` | JSON response body |
| `text` | Response text |
| `headers` | Response headers |
| `all` | Everything together |

## Examples

### Status Only

```bash
$ fasthttp get https://api.example.com/data status
200
```

### JSON Response

```bash
$ fasthttp get https://api.example.com/data json
{"id": 1, "name": "John"}
```

### All Info

```bash
$ fasthttp get https://api.example.com/data all
Status: 200
Elapsed: 234.56ms
Headers: {...}
Body: {...}
```

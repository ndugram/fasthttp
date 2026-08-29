# Команды CLI

Доступные команды CLI.

## HTTP методы

### GET

```bash
fasthttp get https://api.example.com/data
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

## Генерация кода

### codegen

Генерирует fasthttp-клиент из OpenAPI 3.x спеки (локальный файл или URL — JSON или YAML):

```bash
fasthttp codegen openapi.json -o client.py
fasthttp codegen https://api.example.com/openapi.json -o client.py
```

Эндпоинты без path-параметров превращаются в идиоматичные `@app.get`/`@app.post` роуты.
У fasthttp нет динамического роутинга по path-параметрам (URL роута фиксируется
в момент декорирования), поэтому эндпоинты *с* path-параметрами (`/users/{id}`)
генерируются как обычные функции на `AsyncSession`:

```python
@app.get(url="/pets", tags=["pets"], response_model=PetList)
async def list_pets(resp: Response) -> dict:
    return resp.json()

async def get_pet(session: AsyncSession, petId: str) -> dict | None:
    resp = await session.get(f"{base_url}/pets/{petId}")
    return resp.json() if resp else None
```

Pydantic-модели генерируются из `components.schemas` — `$ref` резолвится,
строковые enum превращаются в `Literal[...]`.

!!! note "Ограничения MVP"
    Композиция схем `oneOf`/`anyOf`/`allOf` сводится к `Any`, инлайновые
    (безымянные) вложенные объекты — к `dict[str, Any]` вместо генерации
    вложенной модели. YAML-спеки требуют `pip install fasthttp-client[codegen]`
    (или напрямую `pip install pyyaml`) — для JSON ничего доп. не нужно.

## Формат вывода

Второй аргумент определяет вывод:

| Формат | Описание |
|--------|----------|
| `status` | Только код статуса (по умолчанию) |
| `json` | JSON тело ответа |
| `text` | Текст ответа |
| `headers` | Заголовки ответа |
| `all` | Всё вместе |

## Примеры

```bash
# Только статус
$ fasthttp get https://api.example.com/data status
200

# JSON ответ
$ fasthttp get https://api.example.com/data json
{"id": 1, "name": "John"}
```

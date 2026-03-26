# Зависимости

Справочник по функции Depends.

## Depends()

Создать зависимость:

```python
from fasthttp import Depends


def my_dependency(route, config):
    config.setdefault("headers", {})["X-Custom"] = "value"
    return config


@app.get(url="/data", dependencies=[Depends(my_dependency)])
async def handler(resp):
    return resp.json()
```

## Параметры

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `func` | `Callable` | - | Функция зависимости |
| `use_cache` | `bool` | `True` | Кэшировать результат |
| `scope` | `str` | `"function"` | Область выполнения |

## use_cache

Если `True`, результат кэшируется на время запроса:

```python
async def get_token(route, config):
    token = await fetch_token()
    config["headers"]["Authorization"] = f"Bearer {token}"
    return config


@app.get(url="/api/data", dependencies=[Depends(get_token, use_cache=True)])
async def handler1(resp): ...
```

## Без Depends()

Можно опустить `Depends()`:

```python
# Оба варианта работают одинаково
@app.get(url="/test", dependencies=[Depends(add_auth)])
async def test1(resp): ...


@app.get(url="/test", dependencies=[add_auth])
async def test2(resp): ...
```

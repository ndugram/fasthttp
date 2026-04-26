<p align="center">
  <img src="../logo.png" style="background:white; padding:12px; border-radius:10px; width:350">
</p>
<p align="center">
    <em>Быстрый, простой HTTP-клиент с декораторным роутингом, поддержкой async и красивым логированием.</em>
</p>
<p align="center">
<a href="https://github.com/ndugram/fasthttp/actions/workflows/tests.yml" target="_blank">
    <img src="https://github.com/ndugram/fasthttp/actions/workflows/tests.yml/badge.svg" alt="Tests">
</a>
<a href="https://pypi.org/project/fasthttp-client" target="_blank">
    <img src="https://img.shields.io/pypi/v/fasthttp-client?color=%2334D058&label=pypi%20package" alt="Package version">
</a>
<a href="https://pypi.org/project/fasthttp-client" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/fasthttp-client.svg?color=%2334D058" alt="Supported Python versions">
</a>
<a href="https://codspeed.io/ndugram/fasthttp" target="_blank">
    <img src="https://img.shields.io/endpoint?url=https://codspeed.io/badge.json" alt="CodSpeed">
</a>
</p>

---

**Документация**: <a href="https://fasthttp.ndugram.dev/ru/latest/" target="_blank">https://fasthttp.ndugram.dev/ru/latest/</a>

**Исходный код**: <a href="https://github.com/ndugram/fasthttp" target="_blank">https://github.com/ndugram/fasthttp</a>

---

FastHTTP — это современная **асинхронная HTTP-клиентская библиотека** для Python, построенная поверх **httpx**. Она предоставляет API на основе декораторов — похожий на FastAPI, но для исходящих запросов — со структурированным логированием, middleware, валидацией через Pydantic и встроенным Swagger UI.

Ключевые возможности:

* **Быстрый**: построен на <a href="https://www.python-httpx.org/" target="_blank">httpx</a> с полной поддержкой async и параллельным выполнением запросов.
* **Простой**: определяйте HTTP-запросы как декорированные async-функции, без лишнего кода.
* **Типизированный**: полные аннотации типов; валидация ответов через <a href="https://docs.pydantic.dev/" target="_blank">Pydantic</a>.
* **Логирует**: красочные структурированные логи запросов/ответов со временем выполнения, встроено.
* **Полный**: GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS и GraphQL из коробки.
* **Расширяемый**: middleware, dependency injection, роутеры, lifespan-хуки.
* **Интерактивный**: встроенный Swagger UI через `app.web_run()` для просмотра и выполнения запросов в браузере.
* **HTTP/2**: опциональная поддержка HTTP/2 с автоматическим fallback на HTTP/1.1.

## Требования

Python 3.10+

FastHTTP стоит на плечах гигантов:

* <a href="https://www.python-httpx.org/" target="_blank"><code>httpx</code></a> — асинхронный HTTP-транспорт.
* <a href="https://docs.pydantic.dev/" target="_blank"><code>pydantic</code></a> — валидация и сериализация моделей ответов.
* <a href="https://github.com/ijl/orjson" target="_blank"><code>orjson</code></a> — быстрый парсинг JSON.
* <a href="https://typer.tiangolo.com/" target="_blank"><code>typer</code></a> — CLI-интерфейс.
* <a href="https://www.uvicorn.org/" target="_blank"><code>uvicorn</code></a> — ASGI-сервер для `web_run()`.

## Установка

```console
$ pip install fasthttp-client

---> 100%
```

## Пример

### Создайте файл

Создайте файл `main.py`:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.get(url="https://httpbin.org/get")
async def get_data(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()
```

### Запустите

```console
$ python main.py
```

### Проверьте результат

Вы увидите вывод такого вида:

```
16:09:18.955 │ INFO     │ fasthttp │ ✔ FastHTTP started
16:09:19.519 │ INFO     │ fasthttp │ ✔ GET https://httpbin.org/get [200] 458.26ms
16:09:20.037 │ INFO     │ fasthttp │ ✔ Done in 1.08s
```

Объект `resp` даёт доступ к статусу, заголовкам и телу ответа. `resp.json()` возвращает распарсенный ответ:

```json
{
    "args": {},
    "headers": {
        "Accept": "*/*",
        "Host": "httpbin.org",
        "User-Agent": "python-httpx/0.28.1"
    },
    "origin": "...",
    "url": "https://httpbin.org/get"
}
```

### Интерактивная документация API

Замените `app.run()` на `app.web_run()`:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/users/1")
async def get_user(resp: Response) -> dict:
    return resp.json()


@app.post(url="https://jsonplaceholder.typicode.com/users")
async def create_user(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.web_run()
```

Перейдите на <a href="http://127.0.0.1:8000/docs" target="_blank">http://127.0.0.1:8000/docs</a>.

Вы увидите автоматическую интерактивную документацию API:

![Swagger UI](../photo/swagger_ui_home.png)

Раскройте любой маршрут для просмотра параметров, схем и ожидаемых ответов:

![Swagger UI expanded](../photo/swagger_ui_check_web.png)

Нажмите **Try it out**, чтобы выполнить запрос прямо из браузера и увидеть реальный ответ:

![Swagger UI execute](../photo/swagger_ui_check_execute.png)

### Расширение примера

Измените `main.py`, чтобы использовать больше возможностей FastHTTP. Каждое расширение опирается на предыдущее.

<details markdown="1">
<summary>С Pydantic-моделями ответа...</summary>

Объявите Pydantic-модель и передайте её как `response_model`. FastHTTP автоматически провалидирует и распарсит ответ:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response
from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    email: str


app = FastHTTP()


@app.get(
    url="https://jsonplaceholder.typicode.com/users/1",
    response_model=User,
)
async def get_user(resp: Response) -> User:
    return User(**resp.json())


if __name__ == "__main__":
    app.run()
```

</details>

<details markdown="1">
<summary>С несколькими HTTP-методами...</summary>

Регистрируйте любое количество маршрутов для всех HTTP-методов. FastHTTP выполняет их конкурентно:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP()


@app.get(url="https://httpbin.org/get")
async def get_data(resp: Response) -> dict:
    return resp.json()


@app.post(url="https://httpbin.org/post")
async def post_data(resp: Response) -> dict:
    return resp.json()


@app.put(url="https://httpbin.org/put")
async def put_data(resp: Response) -> dict:
    return resp.json()


@app.patch(url="https://httpbin.org/patch")
async def patch_data(resp: Response) -> dict:
    return resp.json()


@app.delete(url="https://httpbin.org/delete")
async def delete_data(resp: Response) -> int:
    return resp.status_code


@app.head(url="https://httpbin.org/get")
async def head_data(resp: Response) -> int:
    return resp.status


@app.options(url="https://httpbin.org/get")
async def options_data(resp: Response) -> dict:
    return {"allow": resp.headers.get("allow", "")}


if __name__ == "__main__":
    app.run()
```

</details>

<details markdown="1">
<summary>С роутерами...</summary>

Группируйте связанные маршруты в `Router` с общим префиксом или базовым URL, затем подключайте к приложению:

```python
from fasthttp import FastHTTP, Router
from fasthttp.response import Response

users_router = Router(prefix="https://jsonplaceholder.typicode.com")


@users_router.get(url="/users/1")
async def get_user(resp: Response) -> dict:
    return resp.json()


@users_router.get(url="/users/2")
async def get_user_two(resp: Response) -> dict:
    return resp.json()


@users_router.post(url="/users")
async def create_user(resp: Response) -> dict:
    return resp.json()


app = FastHTTP()
app.include_router(users_router)

if __name__ == "__main__":
    app.run()
```

</details>

<details markdown="1">
<summary>С middleware...</summary>

Перехватывайте и изменяйте запросы перед отправкой и ответы после получения:

```python
from fasthttp import FastHTTP
from fasthttp.middleware import BaseMiddleware
from fasthttp.response import Response


class LoggingMiddleware(BaseMiddleware):
    __priority__ = 0
    __methods__ = None
    __enabled__ = True

    async def request(self, method: str, url: str, kwargs: dict) -> dict:
        print(f"→ {method} {url}")
        return kwargs

    async def response(self, response: Response) -> Response:
        print(f"← {response.status}")
        return response


app = FastHTTP(middleware=[LoggingMiddleware()])


@app.get(url="https://httpbin.org/get")
async def get_data(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()
```

</details>

<details markdown="1">
<summary>С dependency injection...</summary>

Используйте `Depends` для переиспользования логики между маршрутами — auth-токены, вычисленные заголовки или любая подготовительная работа:

```python
from fasthttp import FastHTTP, Depends
from fasthttp.response import Response
from fasthttp.types import RequestsOptinal


def auth_headers() -> RequestsOptinal:
    return {"headers": {"Authorization": "Bearer my-token"}}


app = FastHTTP()


@app.get(
    url="https://httpbin.org/get",
    dependencies=[Depends(auth_headers)],
)
async def get_data(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()
```

</details>

<details markdown="1">
<summary>С lifespan...</summary>

Выполняйте инициализацию и очистку вокруг ваших запросов с помощью async context manager:

```python
from contextlib import asynccontextmanager

from fasthttp import FastHTTP
from fasthttp.response import Response


@asynccontextmanager
async def lifespan(app: FastHTTP):
    print("Startup: загружаем учётные данные...")
    app.token = "my-secret-token"  # type: ignore[attr-defined]
    yield
    print("Shutdown: очистка завершена.")


app = FastHTTP(lifespan=lifespan)


@app.get(url="https://httpbin.org/get")
async def get_data(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()
```

</details>

<details markdown="1">
<summary>С GraphQL...</summary>

Используйте `@app.graphql` для отправки запросов и мутаций. Обработчик возвращает тело запроса; FastHTTP отправляет его и передаёт распарсенный ответ:

```python
from fasthttp import FastHTTP
from fasthttp.response import Response


app = FastHTTP()


@app.graphql(url="https://countries.trevorblades.com/graphql")
async def get_countries(resp: Response) -> dict:
    return {
        "query": """
            {
                countries {
                    name
                    code
                    capital
                }
            }
        """
    }


if __name__ == "__main__":
    app.run()
```

</details>

## Опциональные зависимости

* <a href="https://www.python-httpx.org/http2/" target="_blank"><code>httpx[http2]</code></a> — поддержка протокола HTTP/2.

```console
$ pip install fasthttp-client[http2]
```

Включение HTTP/2 для конкретного приложения:

```python
app = FastHTTP(http2=True)
```

Серверы без поддержки HTTP/2 автоматически переходят на HTTP/1.1.

## Лицензия

Этот проект лицензирован на условиях <a href="https://github.com/ndugram/fasthttp/blob/master/LICENSE" target="_blank">лицензии MIT</a>.

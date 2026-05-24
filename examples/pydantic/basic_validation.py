from pydantic import BaseModel

from fasthttp import FastHTTP
from fasthttp.response import Response


class User(BaseModel):
    id: int
    name: str
    username: str


app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/users/1", response_model=User)
async def get_user(resp: Response) -> User:
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/users", response_model=list[User])
async def get_all_users(resp: Response) -> list[User]:
    return resp.json()


if __name__ == "__main__":
    app.run()

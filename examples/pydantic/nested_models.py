from pydantic import BaseModel

from fasthttp import FastHTTP
from fasthttp.response import Response


class Address(BaseModel):
    street: str
    suite: str
    city: str
    zipcode: str


class Company(BaseModel):
    name: str
    catchPhrase: str
    bs: str


class Geo(BaseModel):
    lat: str
    lng: str


class User(BaseModel):
    id: int
    name: str
    username: str
    email: str
    address: Address
    phone: str
    website: str
    company: Company


class Post(BaseModel):
    userId: int
    id: int
    title: str
    body: str


app = FastHTTP()


@app.get(url="https://jsonplaceholder.typicode.com/users/1", response_model=User)
async def get_user_with_details(resp: Response) -> User:
    return resp.json()


@app.get(url="https://jsonplaceholder.typicode.com/posts/1", response_model=Post)
async def get_post(resp: Response) -> Post:
    return resp.json()


if __name__ == "__main__":
    app.run()

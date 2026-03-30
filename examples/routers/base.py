from fasthttp import FastHTTP, Router
from fasthttp.response import Response

app = FastHTTP()
users = Router(base_url="https://", prefix="/users", tags=["users"])


@users.get("/me")
async def get_me(resp: Response) -> dict:
    return resp.json()


@users.get("/list")
async def get_users(resp: Response) -> dict:
    return resp.json()


app.include_router(users)

app.run()
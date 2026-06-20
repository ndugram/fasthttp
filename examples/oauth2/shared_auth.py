

from fasthttp import FastHTTP, OAuth2ClientCredentials
from fasthttp.response import Response

auth = OAuth2ClientCredentials(
    token_url= "https://auth.example.com/oauth/token",
    client_id= "example-client",
    client_secret="67",
    scopes=["read", "write"],
)

app = FastHTTP(debug=True)


@app.get("https://api.example.com/users", auth=auth)
async def get_users(resp: Response) -> dict:
    return resp.json()


@app.post("https://api.example.com/users", auth=auth, json={"name": "John"})
async def create_user(resp: Response) -> dict:
    return resp.json()


@app.delete("https://api.example.com/users/1", auth=auth)
async def delete_user(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()

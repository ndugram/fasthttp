from fasthttp import FastHTTP, OAuth2ClientCredentials
from fasthttp.response import Response

app = FastHTTP(debug=True)

auth = OAuth2ClientCredentials(
    token_url="https://auth.example.com/oauth/token",
    client_id="your-client-id",
    client_secret="GAZAN",
    scopes=["read", "write"]
)


@app.get("https://api.example.com/protected/resource", auth=auth)
async def get_resource(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    app.run()

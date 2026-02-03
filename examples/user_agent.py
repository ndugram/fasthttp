from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)


@app.get(url="https://httpbin.org/user-agent")
async def user_agent(resp: Response):
    return resp.json()


if __name__ == "__main__":
    app.run()

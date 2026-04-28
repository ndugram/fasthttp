from fasthttp import FastHTTP, SessionMiddleware
from fasthttp.response import Response

session = SessionMiddleware()
app = FastHTTP(middleware=session)

@app.get(
    url="https://httpbin.org/cookies/set",
    params={"session_token": "abc123", "user": "alice"},
    tags=["set-cookies"],
)
async def set_cookies(resp: Response) -> dict:
    print(f"Status: {resp.status}")
    print(f"Captured cookies: {session.cookies}")
    return {"status": resp.status}


@app.get(url="https://httpbin.org/cookies", tags=["read-cookies"])
async def read_cookies(resp: Response) -> dict:
    data = resp.json()
    print(f"Server sees cookies: {data.get('cookies')}")
    return data


@app.get(url="https://httpbin.org/cookies", tags=["pre-seeded"])
async def inspect(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    print("=== Setting cookies ===")
    app.run(tags=["set-cookies"])

    print("\n=== Reading cookies (injected by SessionMiddleware) ===")
    app.run(tags=["read-cookies"])

    print(f"\nStored cookies: {session.get_cookies()}")

    session.clear()

    pre_seeded = SessionMiddleware(cookies={"auth_token": "xyz789"})
    app2 = FastHTTP(middleware=pre_seeded)

    @app2.get(url="https://httpbin.org/cookies", tags=["pre-seeded"])
    async def inspect2(resp: Response) -> dict:
        return resp.json()

    print("\n=== Pre-seeded session ===")
    app2.run()
    print(f"Cookies after run: {pre_seeded.get_cookies()}")

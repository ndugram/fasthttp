from fasthttp import CookieJar, FastHTTP
from fasthttp.response import Response

jar = CookieJar()
app = FastHTTP(cookie_jar=jar)


@app.get(
    url="https://httpbin.org/cookies/set",
    params={"session_token": "abc123", "user": "alice"},
    tags=["set"],
)
async def set_cookies(resp: Response) -> dict:
    print(f"Status: {resp.status}")
    return {"status": resp.status}


@app.get(url="https://httpbin.org/cookies", tags=["read"])
async def read_cookies(resp: Response) -> dict:
    data = resp.json()
    print(f"Server sees cookies: {data.get('cookies')}")
    return data




app2 = FastHTTP(cookie_jar=CookieJar({"auth_token": "xyz789", "theme": "dark"}))


@app2.get(url="https://httpbin.org/cookies")
async def inspect(resp: Response) -> dict:
    data = resp.json()
    print(f"Pre-seeded cookies seen by server: {data.get('cookies')}")
    return data




jar3 = CookieJar({"a": "1", "b": "2"})
app3 = FastHTTP(cookie_jar=jar3)


@app3.get(url="https://httpbin.org/get")
async def dummy_request(resp: Response) -> dict:
    return resp.json()


if __name__ == "__main__":
    print("=== Set cookies ===")
    app.run(tags=["set"])

    print(f"\nJar after set: {jar.items()}")

    print("\n=== Read cookies (injected from jar) ===")
    app.run(tags=["read"])

    print(f"\nCookie 'user': {jar.get('user')}")
    jar.clear()
    print(f"Jar after clear: {jar.items()}")

    print("\n=== Pre-seeded jar ===")
    app2.run()

    print("\n=== Inspect jar before request ===")
    print(f"Cookies in jar3: {jar3.items()}")
    app3.run()

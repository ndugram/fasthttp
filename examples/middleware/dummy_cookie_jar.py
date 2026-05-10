from fasthttp import CookieJar, DummyCookieJar, FastHTTP
from fasthttp.response import Response



app_no_cookies = FastHTTP(cookie_jar=DummyCookieJar())
app_with_cookies = FastHTTP(cookie_jar=CookieJar())


@app_no_cookies.get(
    url="https://httpbin.org/cookies/set",
    params={"session_token": "abc123"},
    tags=["set"],
)
async def set_no_capture(resp: Response) -> dict:
    print(f"Status: {resp.status}")
    return {"status": resp.status}


@app_no_cookies.get(url="https://httpbin.org/cookies", tags=["read"])
async def read_no_cookies(resp: Response) -> dict:
    data = resp.json()
    print(f"DummyCookieJar — server sees: {data.get('cookies')}")
    return data


@app_with_cookies.get(
    url="https://httpbin.org/cookies/set",
    params={"session_token": "abc123"},
    tags=["set"],
)
async def set_capture(resp: Response) -> dict:
    return {"status": resp.status}


@app_with_cookies.get(url="https://httpbin.org/cookies", tags=["read"])
async def read_with_cookies(resp: Response) -> dict:
    data = resp.json()
    print(f"CookieJar — server sees: {data.get('cookies')}")
    return data


if __name__ == "__main__":
    print("=== DummyCookieJar: cookies not captured ===")
    app_no_cookies.run(tags=["set"])
    app_no_cookies.run(tags=["read"])

    print("\n=== CookieJar: cookies captured and injected ===")
    app_with_cookies.run(tags=["set"])
    app_with_cookies.run(tags=["read"])

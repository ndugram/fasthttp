from fasthttp import FastHTTP
from fasthttp.response import Response


app = FastHTTP(
    debug=True,
    http2=True,
)


@app.get(url="https://www.google.com/")
async def get_google(resp: Response) -> int:
    print("\nGoogle Request:")
    print(f"  Status: {resp.status}")
    print("Protocol: HTTP/2 (if supported by server)")
    return resp.status


@app.get(url="https://github.com/")
async def get_github(resp: Response) -> int:
    print("\nGitHub Request:")
    print(f"Status: {resp.status}")
    print("Protocol: HTTP/2 (if supported by server)")
    return resp.status


@app.get(url="https://httpbin.org/get")
async def get_httpbin(resp: Response) -> dict:
    print("\nHTTPBin Request:")
    print(f"  Status: {resp.status}")
    print("Protocol: HTTP/1.1 (httpbin doesn't support HTTP/2)")
    return resp.json()


if __name__ == "__main__":
    print("HTTP/2 Example")
    print("Note: Not all servers support HTTP/2.")
    print("If a server doesn't support HTTP/2, it will fall back to HTTP/1.1.")
    print("\nServers that support HTTP/2:")
    print("  - Google: https://www.google.com")
    print("  - GitHub: https://github.com")
    print("  - Many modern websites")
    print("\nServers that don't support HTTP/2:")
    print("  - httpbin.org (uses HTTP/1.1)")
    print()

    app.run()

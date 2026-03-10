from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)


@app.get(url="https://jsonplaceholder.typicode.com/posts/1")
async def successful_request(resp: Response) -> dict:
    print(f"✓ Success! Status: {resp.status}")
    print(f"Response: {resp.json()}")
    return resp.json()


if __name__ == "__main__":
    app.run()

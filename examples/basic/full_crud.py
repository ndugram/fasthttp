from fasthttp import FastHTTP
from fasthttp.response import Response

app = FastHTTP(debug=True)


@app.post(
    url="https://jsonplaceholder.typicode.com/posts",
    json={"title": "New Post", "body": "Content", "userId": 1},
)
async def create(resp: Response) -> dict:
    print(f"POST: {resp.status}")
    return resp.json()


@app.put(
    url="https://jsonplaceholder.typicode.com/posts/1",
    json={"id": 1, "title": "Updated Title", "body": "Updated content", "userId": 1},
)
async def update(resp: Response) -> dict:
    print(f"PUT: {resp.status}")
    return resp.json()


@app.patch(
    url="https://jsonplaceholder.typicode.com/posts/1", json={"title": "Patched Title"}
)
async def patch(resp: Response) -> dict:
    print(f"PATCH: {resp.status}")
    return resp.json()


@app.delete(url="https://jsonplaceholder.typicode.com/posts/1")
async def delete(resp: Response) -> dict:
    print(f"DELETE: {resp.status}")
    return {"deleted": True, "status": resp.status}


if __name__ == "__main__":
    app.run()

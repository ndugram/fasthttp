import asyncio

from fasthttp import AsyncSession


async def main() -> None:
    async with AsyncSession(
        base_url="https://jsonplaceholder.typicode.com",
        headers={"X-App": "fasthttp-session"},
        timeout=10.0,
        security=False,
    ) as session:
        resp = await session.post(
            "/posts",
            json={"title": "new post", "body": "content", "userId": 1},
        )
        if resp:
            print("POST →", resp.status, resp.json())

        resp = await session.put(
            "/posts/1",
            json={"id": 1, "title": "updated", "body": "content", "userId": 1},
        )
        if resp:
            print("PUT →", resp.status)

        resp = await session.patch("/posts/1", json={"title": "patched"})
        if resp:
            print("PATCH →", resp.status, resp.json())

        resp = await session.delete("/posts/1")
        if resp:
            print("DELETE →", resp.status)

        resp = await session.get(
            "/posts/1", timeout=5.0, headers={"Accept": "application/json"}
        )
        if resp:
            print("GET →", resp.status, resp.json())


if __name__ == "__main__":
    asyncio.run(main())

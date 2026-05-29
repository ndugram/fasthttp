import asyncio

from fasthttp import AsyncSession


async def main() -> None:
    async with AsyncSession(
        base_url="https://jsonplaceholder.typicode.com",
        timeout=10.0,
        security=False,
        debug=True,
    ) as session:
        resp = await session.get("/todos/1")
        if resp:
            print(resp.json())

        resp = await session.get("/todos", params={"userId": 1})
        if resp:
            todos = resp.json()
            print(f"fetched {len(todos)} todos")

        resp = await session.post(
            "/posts",
            json={"title": "hello", "body": "world", "userId": 1},
        )
        if resp:
            print(resp.status, resp.json())


if __name__ == "__main__":
    asyncio.run(main())

import asyncio

from fasthttp import AsyncSession


async def main() -> None:
    session = AsyncSession(
        base_url="https://jsonplaceholder.typicode.com",
        security=False,
    )

    await session.open()

    try:
        resp = await session.get("/users/1")
        if resp:
            print(resp.json())

        resp = await session.request("GET", "/users/2")
        if resp:
            print(resp.json())
    finally:
        await session.close()


if __name__ == "__main__":
    asyncio.run(main())

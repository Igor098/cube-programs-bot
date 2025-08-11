import asyncio

from aiohttp import ClientSession


async def test_auth_service():
    async with ClientSession(base_url="http://localhost:8000/v1/") as session:
        async with session.post("bot/admin/login", params={"telegram_id": 2024928561}) as response:
            response.raise_for_status()
            return await response.json()


asyncio.run(test_auth_service())
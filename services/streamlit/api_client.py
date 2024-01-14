import aiohttp


async def make_request(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost'+url) as resp:
            return await resp.json()

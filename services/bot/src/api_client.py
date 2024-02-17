import aiohttp

from config_reader import config


async def make_request(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(config.api_base_url+url) as resp:
            return await resp.json()

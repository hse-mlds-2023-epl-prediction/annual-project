import logging
from aiogram import Bot, Dispatcher, types, F
import asyncio
import aiohttp
import prettytable as pt
from aiogram.filters import Command
from aiogram.enums.parse_mode import ParseMode
from config_reader import config

bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()

@dp.message(F.text, Command('games_today'))
async def games_today(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(config.api_url+'/games-today') as resp:
            json = await resp.json()

            if (len(json)):
                table = pt.PrettyTable(['Home', 'Away', 'Ground'])
                table.align['Home'] = 'l'
                table.align['Away'] = 'l'
                table.align['Ground'] = 'r'

                for item in json:
                    table.add_row([item['Home'], item['Away'], item['Ground']])

                await message.answer(f'<pre>{table}</pre>', parse_mode=ParseMode.HTML)
            else:
                await message.answer('No games tomorrow')

@dp.message(F.text, Command('games_tomorrow'))
async def games_tomorrow(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(config.api_url+'/games-tomorrow') as resp:
            json = await resp.json()

            if (len(json)):
                table = pt.PrettyTable(['Home', 'Away', 'Ground'])
                table.align['Home'] = 'l'
                table.align['Away'] = 'l'
                table.align['Ground'] = 'r'

                for item in json:
                    table.add_row([item['Home'], item['Away'], item['Ground']])

                await message.answer(f'<pre>{table}</pre>', parse_mode=ParseMode.HTML)
            else:
                await message.answer('No games tomorrow')

@dp.message(F.text, Command('games_ten'))
async def games_ten(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(config.api_url+'/games?limit=10') as resp:
            json = await resp.json()

            table = pt.PrettyTable(['Home', 'Away', 'Ground'])
            table.align['Home'] = 'l'
            table.align['Away'] = 'l'
            table.align['Ground'] = 'r'

            for item in json:
                table.add_row([item['Home'], item['Away'], item['Ground']])

            await message.answer(f'<pre>{table}</pre>', parse_mode=ParseMode.HTML)

@dp.message(F.text, Command('start'))
async def start(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(config.api_url) as resp:
            print(resp.status)
            text = await resp.text()

            await message.answer(f"Hello world {text}!")

async def main():
    logging.basicConfig(level=logging.DEBUG)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

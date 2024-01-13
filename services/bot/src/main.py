import logging
from aiogram import Bot, Dispatcher, types, F
import asyncio
import aiohttp
from aiogram.filters import Command
from aiogram.enums.parse_mode import ParseMode
from config_reader import config
from tabulate import tabulate
from app import game_today, game_tomorrow, return_game
from prettytable import PrettyTable
import pandas as pd


bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()


@dp.message(F.text, Command('games_today'))
async def games_today(message: types.Message):
    df = game_today()
    df.reset_index(drop=True, inplace=True)

    if df.shape[0] != 0:
        df = tabulate(df, headers='keys', tablefmt='fancy_grid')
        await message.answer(df, parse_mode='Markdown')
    else:
        await message.answer('No games today')


@dp.message(F.text, Command('games_tomorrow'))
async def games_tomorrow(message: types.Message):
    df = game_tomorrow()
    df.reset_index(drop=True, inplace=True)

    if df.shape[0] != 0:
        df = tabulate(df, headers='keys', tablefmt='fancy_grid')
        await message.answer(df, parse_mode='Markdown')
    else:
        await message.answer('No games tomorrow')


@dp.message(F.text, Command('games_ten'))
async def games_ten(message: types.Message):
    df = return_game()
    df = df.iloc[:10, :].drop('gameDate', axis=1)
    df.reset_index(drop=True, inplace=True)

    df = tabulate(df, headers='keys', tablefmt='fancy_grid')
    await message.answer(df, parse_mode='Markdown')

@dp.message(F.text, Command('start'))
async def start(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:80/') as resp:
            print(resp.status)
            text = await resp.text()

            await message.answer(f"Hello world {text}!")

async def main():
    logging.basicConfig(level=logging.DEBUG)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

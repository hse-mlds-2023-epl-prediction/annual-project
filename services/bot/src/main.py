import logging
from aiogram import Bot, Dispatcher, types, F
import asyncio
import aiohttp
import prettytable as pt
from aiogram.filters import Command
from aiogram.enums.parse_mode import ParseMode
from config_reader import config
from tabulate import tabulate
from app import game_today, game_tomorrow, return_game
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
    # table = pt.PrettyTable(['Symbol', 'Price', 'Change'])
    # table.align['Symbol'] = 'l'
    # table.align['Price'] = 'r'
    # table.align['Change'] = 'r'
    #
    # data = [
    #     ('ABC', 20.85, 1.626),
    #     ('DEF', 78.95, 0.099),
    #     ('GHI', 23.45, 0.192),
    #     ('JKL', 98.85, 0.292),
    # ]
    # for symbol, price, change in data:
    #     table.add_row([symbol, f'{price:.2f}', f'{change:.3f}'])
    #
    # await message.answer(f'<pre>{table}</pre>', parse_mode=ParseMode.HTML)


    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:80/games') as resp:

            json = await resp.json()
            print('json', json)
            table = pt.PrettyTable(['Home', 'Away', 'Ground'])
            # table.align['Symbol'] = 'l'
            # table.align['Price'] = 'r'
            # table.align['Change'] = 'r'
            #
            # data = [
            #     ('ABC', 20.85, 1.626),
            #     ('DEF', 78.95, 0.099),
            #     ('GHI', 23.45, 0.192),
            #     ('JKL', 98.85, 0.292),
            # ]
            for item in json:
                table.add_row([item['Home'], item['Away'], item['Ground']])

            await message.answer(f'<pre>{table}</pre>', parse_mode=ParseMode.HTML)

    # df = return_game()
    # df = df.iloc[:10, :].drop('gameDate', axis=1)
    # df.reset_index(drop=True, inplace=True)

            #df = tabulate(df, headers='keys', tablefmt='fancy_grid')
            #await message.answer(df, parse_mode='Markdown')

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

import logging
from aiogram import Bot, Dispatcher, types, F
import asyncio
from aiogram.filters import Command
from aiogram.enums.parse_mode import ParseMode
from config_reader import config
from api_client import make_request
from table_formator import format_games_table, format_stats_table, \
      format_games_with_predict_table

bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()


@dp.message(F.text, Command('games_today'))
async def games_today(message: types.Message):
    json = await make_request('/games-today')
    if len(json):
        table = format_games_table(json)
        await message.answer(f'<pre>{table}</pre>', parse_mode=ParseMode.HTML)
    else:
        await message.answer('No games today')


@dp.message(F.text, Command('games_tomorrow'))
async def games_tomorrow(message: types.Message):
    json = await make_request('/games-tomorrow')

    if len(json):
        table = format_games_table(json)
        await message.answer(f'<pre>{table}</pre>', parse_mode=ParseMode.HTML)
    else:
        await message.answer('No games tomorrow')


@dp.message(F.text, Command('games_ten'))
async def games_ten(message: types.Message):
    json = await make_request('/games?limit=10')

    if len(json):
        table = format_games_table(json)
        await message.answer(f'<pre>{table}</pre>', parse_mode=ParseMode.HTML)
    else:
        await message.answer('No games')


@dp.message(F.text, Command('stats'))
async def stats(message: types.Message):
    json = await make_request('/stats')

    if len(json):
        table = format_stats_table(json)
        await message.answer(f'<pre>{table}</pre>', parse_mode=ParseMode.HTML)
    else:
        await message.answer('No stats')


@dp.message(F.text, Command('start'))
async def start(message: types.Message):
    await message.answer(
        "<b>Привет!</b>\n\n"
        """Это tg bot команды проекта
          «Предсказательные модели для игроков и команд EPL»\n\n"""
        "Список доступных команд:\n"
        "/stats - Статистика команд\n"
        "/games_ten - Посмотреть 10 следующих матчей\n"
        "/games_today - Посмотреть матчи на сегодня\n"
        "/games_tomorrow - Посмотреть матчи на завтра\n"
        "/ten_predict - Предсказать 10 следующих матчей\n"
        "/today_predict - Предсказать матчи на сегодня\n"
        "/tomorrow_predict - Предсказать матчи на завтра\n",
        parse_mode="HTML"
    )


@dp.message(F.text, Command('tomorrow_predict'))
async def tomorrow_predict(message: types.Message):
    json = await make_request('/games-tomorrow-predict')

    if len(json):
        table = format_games_with_predict_table(json)
        await message.answer(f'<pre>{table}</pre>', parse_mode=ParseMode.HTML)
    else:
        await message.answer('No games tomorrow')


@dp.message(F.text, Command('today_predict'))
async def today_predict(message: types.Message):
    json = await make_request('/games-today-predict')
    if len(json):
        table = format_games_with_predict_table(json)
        await message.answer(f'<pre>{table}</pre>', parse_mode=ParseMode.HTML)
    else:
        await message.answer('No games today')


@dp.message(F.text, Command('ten_predict'))
async def ten_predict(message: types.Message):
    json = await make_request('/games-predict')
    if len(json):
        table = format_games_with_predict_table(json)
        await message.answer(f'<pre>{table}</pre>', parse_mode=ParseMode.HTML)
    else:
        await message.answer('No games')


async def main():
    logging.basicConfig(level=logging.DEBUG)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

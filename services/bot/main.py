import asyncio
import aiohttp
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token="BOT_TOKEN")
# Диспетчер
dp = Dispatcher()

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    print(message.from_user.model_dump_json())

    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:80/') as resp:
            print(resp.status)
            text = await resp.text()

            await message.answer(f"Hello {text}!")

# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

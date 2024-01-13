import asyncio
import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message,
)

# from handlers import router
router = Router()


@router.message(Command("start"))
async def start_handler(msg: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Show",
                             callback_data='show'),
        InlineKeyboardButton(text="Help", callback_data='help'),
    ]])
    await msg.answer("Привет! Я умею предсказывать исходы матчей между командами АПЛ.", reply_markup=keyboard)


@router.message(Command("show"))
async def message_handler(msg: Message):
    await msg.answer(f"Твой ID: {msg.from_user.id}")


@router.message(Command("help"))
async def message_handler(msg: Message):
    await msg.answer("""
/help - Посмотреть весь список команд
/predict - Предсказать исход матча""")


@router.message()
async def message_handler(msg: Message):
    await msg.answer('Я понимаю только команды. Если забыл команды, отправь мне /help для полного списка команд')


async def main():
    bot = Bot(token='6952794527:AAFRFbn_R8zU8MJzX3Xbx6LYPh1bCmIShCk',
              parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

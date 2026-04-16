from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.inline import menu_kb

router = Router()

@router.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Привет! Я не дам спиздить Ваши сервера:",
        reply_markup=menu_kb()
    )
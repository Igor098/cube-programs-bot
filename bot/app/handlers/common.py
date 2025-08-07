from aiogram import Router

from aiogram.filters import CommandStart
from aiogram.types import Message

from filters.chat_type import ChatTypeFilter
from keyboards.main import main_keyboard


router = Router()

@router.message(CommandStart(), ChatTypeFilter(chat_type=["private"]))
async def start_command(message: Message) -> None:
    await message.answer(
        "Привет-привет! 🤖 Я - виртуальный ассистент Центра \"IT-куб\", У нас вы можете пройти бесплатное обучение по самым востребованным IT-направлениям!  Готов рассказать о наших программах и подсказать, как записаться.",
        reply_markup=main_keyboard()
    )
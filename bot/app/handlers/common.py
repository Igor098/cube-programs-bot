from aiogram import Router

from aiogram.filters import CommandStart
from aiogram.types import Message

from loguru import logger

from app.tokens import get_token
from app.filters.chat_type import ChatTypeFilter
from app.keyboards.main import main_keyboard


router = Router()

@router.message(CommandStart(), ChatTypeFilter(chat_type=["private"]))
async def start_command(message: Message) -> None:
    token = get_token(message.from_user.id)
    is_admin = True if token else False
    await message.answer(
        "Привет-привет! 🤖 Я - виртуальный ассистент Центра \"IT-куб\", У нас вы можете пройти бесплатное обучение по самым востребованным IT-направлениям!  Готов рассказать о наших программах и подсказать, как записаться.",
        reply_markup=main_keyboard(is_admin=is_admin)
    )
    try:
        await message.delete()
    except Exception as e:
        logger.error(f"Не удалось удалить сообщение. Ошибка: {e}")
        pass
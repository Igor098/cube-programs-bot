from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.config import settings

def build_question_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Перейти в канал", url=settings.CHANNEL_URL)],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="pick:cancel")],
    ])
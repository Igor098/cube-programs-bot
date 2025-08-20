from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    kb_buttons = [
        [KeyboardButton(text="🔍 Подобрать программу"), KeyboardButton(text="📋 Список программ")],
        [KeyboardButton(text="📝 Как записаться"), KeyboardButton(text="❓ Задать вопрос")]
    ]

    if is_admin:
        kb_buttons.append([KeyboardButton(text="📝 Обновить список программ")])

    keyboard = ReplyKeyboardMarkup(keyboard=kb_buttons, resize_keyboard=True)
    
    return keyboard

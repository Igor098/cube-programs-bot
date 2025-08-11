from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_keyboard():
    kb_buttons = [
        [KeyboardButton(text="🔍 Подобрать программу"), KeyboardButton(text="📋 Список программ")],
        [KeyboardButton(text="📝 Как записаться"), KeyboardButton(text="🔑 Войти")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb_buttons, resize_keyboard=True)
    
    return keyboard

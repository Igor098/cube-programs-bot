from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def kb_pick_age() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🧒 5 лет",  callback_data="pick:age:5"),
            InlineKeyboardButton(text="🧒 6 лет", callback_data="pick:age:6"),
            InlineKeyboardButton(text="🧒 7 лет", callback_data="pick:age:7"),
        ],
        [
            InlineKeyboardButton(text="👦 8 лет", callback_data="pick:age:8"),
            InlineKeyboardButton(text="👦 9 лет", callback_data="pick:age:9"),
            InlineKeyboardButton(text="👦 10 лет", callback_data="pick:age:10"),
        ],
        [
            InlineKeyboardButton(text="🧑 11 лет", callback_data="pick:age:11"),
            InlineKeyboardButton(text="🧑 12 лет", callback_data="pick:age:12"),
            InlineKeyboardButton(text="🧑 13 лет", callback_data="pick:age:13"),
        ],
        [
            InlineKeyboardButton(text="🧔 14 лет", callback_data="pick:age:14"),
            InlineKeyboardButton(text="🧔 15 лет", callback_data="pick:age:15"),
            InlineKeyboardButton(text="🧔 16 лет", callback_data="pick:age:16"),
        ],
        [
            InlineKeyboardButton(text="🧔 17 лет", callback_data="pick:age:17"),
        ],  
        [
            InlineKeyboardButton(text="❌ Отмена", callback_data="pick:cancel"),
        ]
    ])

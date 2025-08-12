from math import ceil
from typing import List, TypeAlias
from utils.callback_data import encode_detail, encode_list, encode_pick_page
from models import ProgramWithId
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


AGE_RESULTS_LIMIT = 10
Rows: TypeAlias = List[List[InlineKeyboardButton]]

def _short(text: str, limit: int = 48) -> str:
    clean = " ".join(str(text).split())
    return clean if len(clean) <= limit else clean[:limit - 1] + "…"

def build_programs_age_manage_rows(version: int) -> Rows:
    return [
        [
            InlineKeyboardButton(text="🔁 Выбрать другой возраст", callback_data="pick:again"),
            InlineKeyboardButton(text="📋 Весь список", callback_data=encode_list(0, version)),
        ],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="pick:cancel")],
    ]

def build_programs_age_manage_kb(version: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=build_programs_age_manage_rows(version))

def build_programs_age_kb(
    items: List[ProgramWithId],
    age: int,
    page: int,
    version: int,
    limit: int = AGE_RESULTS_LIMIT,
) -> InlineKeyboardMarkup:
    total = len(items)
    pages = max(1, ceil(total / limit))
    page = max(0, min(page, pages - 1))

    start = page * limit
    slice_ = items[start:start+limit]

    rows: list[list[InlineKeyboardButton]] = []
    for p in slice_:
        title = _short(getattr(p, "name", f"Программа #{p.id}"))
        rows.append([InlineKeyboardButton(text=title, callback_data=encode_detail(page, p.id, version))])

    # Навигация
    nav: list[InlineKeyboardButton] = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=encode_pick_page(age, page - 1, version)))
    nav.append(InlineKeyboardButton(text=f"🔄 {page+1}/{pages}", callback_data=encode_pick_page(age, page, version)))
    if page < pages - 1:
        nav.append(InlineKeyboardButton(text="➡️ Далее", callback_data=encode_pick_page(age, page + 1, version)))
    rows.append(nav)

    # Общие действия
    rows.extend(build_programs_age_manage_rows(version))

    return InlineKeyboardMarkup(inline_keyboard=rows)


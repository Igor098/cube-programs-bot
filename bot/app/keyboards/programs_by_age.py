from math import ceil
from typing import List, TypeAlias

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.utils.callback_data import encode_detail, encode_list, encode_pick_page
from app.models import ProgramWithId
from app.utils.formatters import format_program_line


AGE_RESULTS_LIMIT = 10
Rows: TypeAlias = List[List[InlineKeyboardButton]]


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
        rows.append([InlineKeyboardButton(text=format_program_line(p), callback_data=encode_detail(page, p.id, version))])

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


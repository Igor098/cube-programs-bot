from typing import List, TypeAlias
from utils.callback_data import encode_detail, encode_list
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
    version: int,
    limit: int = AGE_RESULTS_LIMIT,
    page_for_detail: int = 0
) -> InlineKeyboardMarkup:
    rows = []
    for p in items[:limit]:
        title = _short(getattr(p, "name", f"Программа #{p.id}"))
        rows.append([InlineKeyboardButton(text=title, callback_data=encode_detail(page_for_detail, p.id, version))])
    
    manage_kb = build_programs_age_manage_rows(version=version)
    rows.extend(manage_kb)
    
    return InlineKeyboardMarkup(inline_keyboard=rows)


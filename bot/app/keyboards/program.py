from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.utils.callback_data import encode_enroll, encode_list, encode_detail
from app.utils.formatters import format_program_line

def _chunk(items, n):
    for i in range(0, len(items), n):
        yield items[i:i+n]

def build_programs_kb(items, page, pages, ver, cols: int = 1) -> InlineKeyboardMarkup:
    rows = []

    for row_items in _chunk(items, cols):
        row = []
        for p in row_items:
            row.append(InlineKeyboardButton(
                text=format_program_line(p),
                callback_data=encode_detail(page, p.id, ver)
            ))
        rows.append(row)

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=encode_list(page - 1, ver)))
    nav.append(InlineKeyboardButton(text="🔄 Обновить", callback_data=encode_list(page, ver)))
    if page < pages - 1:
        nav.append(InlineKeyboardButton(text="➡️ Далее", callback_data=encode_list(page + 1, ver)))
    rows.append(nav)
    rows.append([InlineKeyboardButton(text="❌ Отмена", callback_data="pick:cancel")])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_open_programs_kb(version: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Открыть список программ", callback_data=encode_list(0, version))],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="pick:cancel")]
    ])


def build_detail_kb(
    page: int,
    ver: int,
    program_id: int,
    navigator_link: str | None,
    back_cb: str | None = None,
) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text="⬅️ Назад", callback_data=back_cb or encode_list(page, ver))]]
    if navigator_link:
        rows.append([InlineKeyboardButton(text="📋 Записаться", callback_data=encode_enroll(page, program_id, ver))])
    rows.append([InlineKeyboardButton(text="🔄 Обновить", callback_data=encode_detail(page, program_id, ver))])
    return InlineKeyboardMarkup(inline_keyboard=rows)
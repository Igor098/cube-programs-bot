from aiogram import F
from loguru import logger
from filters.callback_action import ActionFilter
from keyboards.program import build_detail_kb, build_programs_keyboard
from utils.formatters import build_list_message, format_program_caption_html
from states.programs_store_impl import ProgramStore
from utils.callback_data import CallbackPayload, InvalidCallbackPayload, encode_list
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from html import escape as html_escape

from aiogram import Router


router = Router()

def _same_markup(a, b) -> bool:
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False

    return a.model_dump(exclude_none=True) == b.model_dump(exclude_none=True)


from aiogram.exceptions import TelegramBadRequest

async def _edit_text_or_replace(call, text: str, kb):
    """
    Пытается отредактировать текст, если текущее сообщение текстовое.
    Если это медиа (нет text), удаляет и отправляет новое текстовое сообщение.
    """
    if not call.message.text:
        try:
            await call.message.delete()
        except TelegramBadRequest:
            pass
        return await call.message.answer(text, parse_mode="HTML", reply_markup=kb, disable_notification=True)

    try:
        return await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    except TelegramBadRequest as e:
        if "no text in the message to edit" in str(e).lower():
            try:
                await call.message.delete()
            except TelegramBadRequest:
                pass
            return await call.message.answer(text, parse_mode="HTML", reply_markup=kb, disable_notification=True)

        if "message is not modified" in str(e).lower():
            await call.answer("Уже актуально")
            return
        raise


@router.message(F.text.contains("Список программ"))
async def handle_show_programs(message: Message, store: ProgramStore):
    logger.info("Запрос списка программ")

    ver = await store.get_version()
    logger.info(f"Версия: {ver}")
    total = await store.count()
    logger.info(f"Всего программ: {total}")
    pages = await store.page_count()
    logger.info(f"Страниц: {pages}")
    page = 0
    logger.info(f"Текущая страница: {page}")
    
    items = await store.get_page(page)

    start_text = build_list_message(total, page, pages)
    kb = build_programs_keyboard(items, page, pages, ver, cols=1)

    await message.answer(start_text, parse_mode="HTML", reply_markup=kb)
    

@router.callback_query(ActionFilter("p"))
async def on_cb(call: CallbackQuery, store: ProgramStore):
    try:
        logger.info(f"Разбор колбэка списка: {call.data}")
        payload = CallbackPayload.parse(call.data)
    except InvalidCallbackPayload as e:
        logger.error(f"Ошибка разбора данных колбэка: {e}")
        await call.answer("Кнопка устарела или повреждена", show_alert=True)
        return

    current = await store.get_version()
    page = max(0, payload.page or 0)

    if payload.version != current:
        await call.answer("Данные обновились, перерисовываю…", show_alert=False)
        items = await store.get_page(page)
        total = await store.count()
        pages = await store.page_count()
        new_text = build_list_message(total, page, pages)
        new_kb = build_programs_keyboard(items, page, pages, current, cols=1)

        if (call.message.html_text or call.message.text) == new_text:
            try:
                await call.message.edit_reply_markup(reply_markup=new_kb)
            except TelegramBadRequest:
                pass
            return

        try:
            await _edit_text_or_replace(call, new_text, new_kb)
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                await call.answer("Уже актуально")
        return

    if payload.action == "p":
        items = await store.get_page(page)
        total = await store.count()
        pages = await store.page_count()

        new_text = build_list_message(total, page, pages)
        new_kb = build_programs_keyboard(items, page, pages, current, cols=1)

        old_text = call.message.html_text or call.message.text
        old_kb = call.message.reply_markup

        if new_text == old_text and _same_markup(new_kb, old_kb):
            await call.answer("Уже актуально")
            return

        try:
            await _edit_text_or_replace(call, new_text, new_kb)
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                await call.answer("Уже актуально")
            else:
                raise



@router.callback_query(ActionFilter("d"))
async def on_detail(call: CallbackQuery, store: ProgramStore):
    try:
        payload = CallbackPayload.parse(call.data)
    except InvalidCallbackPayload:
        await call.answer("Кнопка устарела или повреждена", show_alert=True)
        return
    if payload.action != "d":
        return

    current = await store.get_version()
    page = max(0, payload.page or 0)

    if payload.version != current:
        await call.answer("Данные обновились, перерисовываю…")
        items = await store.get_page(page)
        total = await store.count()
        pages = await store.page_count()
        start_text = build_list_message(total, page, pages)
        kb = build_programs_keyboard(items, page, pages, current)  # твой билдер
        try:
            await _edit_text_or_replace(call, start_text, kb)
        except TelegramBadRequest:
            pass
        return

    p = await store.get_program_by_id(payload.program_id)
    if not p:
        items = await store.get_page(page)
        total = await store.count()
        pages = await store.page_count()
        start_text = build_list_message(total, page, pages)
        kb = build_programs_keyboard(items, page, pages, current)
        await _edit_text_or_replace(call, start_text, kb)
        return

    kb = build_detail_kb(page, current, p.id, getattr(p, "navigator_link", None))

    try:
        await call.message.delete()
    except TelegramBadRequest:
        logger.error("Ошибка при удалении сообщения", exc_info=True)
        pass

    caption = format_program_caption_html(p)
    photo_url = getattr(p, "image_url", None)

    if photo_url:
        try:
            await call.message.answer_photo(
                photo=photo_url,
                caption=caption,
                parse_mode="HTML",
                reply_markup=kb,
                disable_notification=True,
            )
            return
        except TelegramBadRequest:
            logger.error("Ошибка при отправке фото", exc_info=True)
            pass

    await call.message.answer(
        text=caption,
        parse_mode="HTML",
        reply_markup=kb,
        disable_notification=True,
    )
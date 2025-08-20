from math import ceil
from aiogram import F
from loguru import logger
from services.programs_sync import sync_programs_from_api
from keyboards.main import main_keyboard
from services.program_service import get_programs_list
from tokens import get_token
from keyboards.question import build_question_kb
from keyboards.pick_age import kb_pick_age
from keyboards.programs_by_age import build_programs_age_kb
from states.pick_age import PickAge
from services.file_service import get_enroll_blank
from filters.callback_action import ActionFilter
from keyboards.program import build_detail_kb, build_open_programs_kb, build_programs_kb
from utils.formatters import build_enroll_message, build_enroll_question_message, build_list_message, build_pick_age_intro_html, format_program_caption_html, format_question_html
from states.programs_store_impl import ProgramStore
from utils.callback_data import CallbackPayload, InvalidCallbackPayload, encode_pick_return
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from aiogram import Router


router = Router()
AGE_RESULTS_LIMIT = 10

def _same_markup(a, b) -> bool:
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False

    return a.model_dump(exclude_none=True) == b.model_dump(exclude_none=True)


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
async def handle_show_programs(message: Message, store: ProgramStore, state: FSMContext):
    logger.info("Запрос списка программ")

    ver = await store.get_version()
    logger.info(f"Версия: {ver}")
    total = await store.count()
    logger.info(f"Всего программ: {total}")
    pages = await store.page_count()
    logger.info(f"Страниц: {pages}")
    page = 0
    logger.info(f"Текущая страница: {page}")
    await state.clear()
    
    items = await store.get_page(page)

    start_text = build_list_message(total, page, pages)
    kb = build_programs_kb(items, page, pages, ver, cols=1)

    await message.answer(start_text, parse_mode="HTML", reply_markup=kb)
    try:
        await message.delete()
    except Exception as e:
        logger.error(f"Не удалось удалить сообщение. Ошибка: {e}")
        pass
    

@router.message(F.text.contains("Как записаться"))
async def handle_enroll_question(message: Message, store: ProgramStore, state: FSMContext):
    version = await store.get_version()
    text = build_enroll_question_message()
    kb = build_open_programs_kb(version)
    
    await state.clear()

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=kb,
        disable_web_page_preview=True
        )
    try:
        await message.delete()
    except Exception as e:
        logger.error(f"Не удалось удалить сообщение. Ошибка: {e}")
        pass
    
    
@router.message(F.text.contains("Подобрать программу"))
async def handle_enroll_question(message: Message, state: FSMContext):
    text = build_pick_age_intro_html()
    kb = kb_pick_age()
    
    await state.clear()

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=kb,
        disable_web_page_preview=True
        )
    try:
        await message.delete()
    except Exception as e:
        logger.error(f"Не удалось удалить сообщение. Ошибка: {e}")
        pass
    
    
@router.message(F.text.contains("Задать вопрос"))
async def handle_ask_question(message: Message, state: FSMContext):
    text = format_question_html()
    kb = build_question_kb()
    
    await state.clear()
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=kb
    )
    try:
        await message.delete()
    except Exception as e:
        logger.error(f"Не удалось удалить сообщение. Ошибка: {e}")
        pass
    

@router.message(F.text.contains("Обновить список программ"))
async def handle_ask_question(message: Message, store: ProgramStore, state: FSMContext):
    token = get_token(message.from_user.id)
    is_admin = True if token else False
    if not is_admin:
        await message.answer("Вы не авторизованы в системе или закончилось время авторизации. Для повторной авторизации используйте команду: /login", parse_mode="HTML")
        return
    
    _, msg = await sync_programs_from_api()
    
    await state.clear()
    await message.answer(
        msg,
        parse_mode="HTML",
        reply_markup=main_keyboard(is_admin=is_admin)
    )
    try:
        await message.delete()
    except Exception as e:
        logger.error(f"Не удалось удалить сообщение. Ошибка: {e}")
        pass
    

@router.callback_query(ActionFilter("list"))
async def on_cb(call: CallbackQuery, store: ProgramStore, state: FSMContext):
    try:
        logger.info(f"Разбор колбэка списка: {call.data}")
        payload = CallbackPayload.parse(call.data)
    except InvalidCallbackPayload as e:
        logger.error(f"Ошибка разбора данных колбэка: {e}")
        await call.answer("Кнопка устарела или повреждена", show_alert=True)
        return
    await state.clear()
    current = await store.get_version()
    page = max(0, payload.page or 0)

    if payload.version != current:
        await call.answer("Данные обновились, перерисовываю…", show_alert=False)
        items = await store.get_page(page)
        total = await store.count()
        pages = await store.page_count()
        new_text = build_list_message(total, page, pages)
        new_kb = build_programs_kb(items, page, pages, current, cols=1)

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

    if payload.action == "list":
        items = await store.get_page(page)
        total = await store.count()
        pages = await store.page_count()

        new_text = build_list_message(total, page, pages)
        new_kb = build_programs_kb(items, page, pages, current, cols=1)

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


@router.callback_query(ActionFilter("detail"))
async def on_detail(call: CallbackQuery, state: FSMContext, store: ProgramStore):
    try:
        logger.info(f"Разбор колбэка деталей: {call.data}")
        payload = CallbackPayload.parse(call.data)
    except InvalidCallbackPayload:
        await call.answer("Кнопка устарела или повреждена", show_alert=True)
        return
    if payload.action != "detail":
        return

    current = await store.get_version()
    page = max(0, payload.page or 0)

    if payload.version != current:
        await call.answer("Данные обновились, перерисовываю…")
        items = await store.get_page(page)
        total = await store.count()
        pages = await store.page_count()
        start_text = build_list_message(total, page, pages)
        kb = build_programs_kb(items, page, pages, current)
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
        kb = build_programs_kb(items, page, pages, current)
        await _edit_text_or_replace(call, start_text, kb)
        return
    
    back_cb = None
    if await state.get_state() == PickAge.results:
        data = await state.get_data()
        age = data.get("age_filter"); page = data.get("age_page", 0)
        if isinstance(age, int) and isinstance(page, int):
            back_cb = encode_pick_return(age, page)

    kb = build_detail_kb(page, current, p.id, getattr(p, "navigator_link", None), back_cb=back_cb)

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
    

@router.callback_query(ActionFilter("enroll"))
async def on_enroll(call: CallbackQuery, store: ProgramStore):
    try:
        logger.info(f"Разбор колбэка записи: {call.data}")
        payload = CallbackPayload.parse(call.data)
    except InvalidCallbackPayload:
        await call.answer("Кнопка устарела или повреждена", show_alert=True)
        return

    program = await store.get_program_by_id(payload.program_id)
    if not program:
        await call.answer("Программа не найдена", show_alert=True)
        return

    text = build_enroll_message(p=program)

    await call.message.answer(text, parse_mode="HTML",   disable_web_page_preview=True)

    file = await get_enroll_blank()
    
    await call.message.answer_document(file)
    await call.answer()
    

@router.callback_query(F.data.regexp(r"^pick:age:\d{1,2}$"))
async def on_pick_age(call: CallbackQuery, state: FSMContext, store: ProgramStore):
    age = int(call.data.rsplit(":", 1)[-1])
    await state.update_data(age_filter=age, age_page=0)
    await state.set_state(PickAge.results)

    ver = await store.get_version()
    items = await store.get_programs_by_age(age)

    kb = build_programs_age_kb(items, age=age, page=0, version=ver, limit=AGE_RESULTS_LIMIT)
    text = f"Подходящих программ: <b>{len(items)}</b>. Выберите нужную:"
    await _edit_text_or_replace(call, text, kb)
    await call.answer()

@router.callback_query(F.data.regexp(r"^pick:page:(\d{1,2}):(\d{1,3}):(\d+)$"))
async def on_pick_page(call: CallbackQuery, state: FSMContext, store: ProgramStore):
    _, _, age_str, page_str, ver_str = call.data.split(":")
    age = int(age_str); page = int(page_str); ver = int(ver_str)

    items = await store.get_programs_by_age(age)
    pages = max(1, ceil(len(items) / AGE_RESULTS_LIMIT))
    page = max(0, min(page, pages - 1))

    await state.update_data(age_filter=age, age_page=page)
    await state.set_state(PickAge.results)

    kb = build_programs_age_kb(items, age=age, page=page, version=ver, limit=AGE_RESULTS_LIMIT)
    text = f"Подходящих программ: <b>{len(items)}</b>. Выберите нужную:"
    await _edit_text_or_replace(call, text, kb)
    await call.answer()

@router.callback_query(F.data.startswith("pick:return:"))
async def on_pick_return(call: CallbackQuery, state: FSMContext, store: ProgramStore):
    parts = call.data.split(":")
    try:
        age = int(parts[2]); page = int(parts[3])
    except (IndexError, ValueError):
        await call.answer("Не удалось вернуться к результатам", show_alert=True); return

    ver = await store.get_version()
    items = await store.get_programs_by_age(age)

    kb = build_programs_age_kb(items, age=age, page=page, version=ver, limit=AGE_RESULTS_LIMIT)
    text = f"Подходящих программ: <b>{len(items)}</b>. Выберите нужную:"
    try:
        await _edit_text_or_replace(call, text, kb)
    except TelegramBadRequest:
        await call.message.answer(text, parse_mode="HTML", reply_markup=kb, disable_notification=True)
    await state.update_data(age_filter=age, age_page=page)
    await state.set_state(PickAge.results)
    await call.answer()

@router.callback_query(F.data == "pick:again")
async def on_pick_again(call: CallbackQuery, state: FSMContext):
    await state.set_state(PickAge.age)
    await _edit_text_or_replace(call, "<b>Подберём программу по возрасту</b>.\n\nВыберите подходящий возраст:",
                                kb_pick_age())
    await call.answer()


@router.callback_query(F.data == "pick:cancel")
async def on_pick_cancel(call: CallbackQuery, state: FSMContext):
    try:
        await state.clear()
        await call.message.delete()
    except TelegramBadRequest:
        pass
    await call.answer("Отмена")
        
# import json
# from aiogram import F, Router
# from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, CallbackQuery
# from aiogram.filters import Command
# from loguru import logger

# from services.program_service import add_program, get_programs_list
# from tokens import get_token


# router = Router()


# @router.message(Command("add_program"))
# async def handle_add_program(message: Message):
#     web_app = WebAppInfo(url="https://fl.greatdragonx.su:8000/?program_id=4")
#     keyboard = ReplyKeyboardMarkup(
#         keyboard=[
#             [KeyboardButton(text="➕ Добавить программу", web_app=web_app)]
#         ],
#         resize_keyboard=True
#     )
#     await message.answer(
#         "Нажми на кнопку ниже, чтобы добавить новую программу 👇",
#         reply_markup=keyboard
#     )
    
# @router.message(Command("show_id"))
# async def show_id(message: Message):
#     my_id = message.from_user.id
#     await message.answer(
#         f"Ваш ID: {my_id}",
#     )
    
# @router.message(F.web_app_data)
# async def handle_web_app_data(message: Message):
#     try:
#         user_id = message.from_user.id
#         token = get_token(user_id)
#         data = json.loads(message.web_app_data.data)

#         data["min_age"] = int(data.get("min_age", 0))
#         data["max_age"] = int(data.get("max_age", 0))
#         # ← ТУТ ТВОИ ДАННЫЕ из формы!
#         # Теперь data — это dict с полями формы
#         # Можно отправить их на backend, сохранить в базу и т.д.
#         logger.info(f"Данные получены: {data}")
#         await add_program(token=token, program_data=data)
#     except Exception as e:
#         await message.answer(f"Ошибка при обработке данных из WebApp: {e}")
#         # Можно залогировать ошибку

# @router.message(F.text.contains("Список программ"))
# async def handle_show_programs(message: Message):
#     logger.info("Запрос списка программ")

#     try:
#         programs = await get_programs_list()
#     except Exception as e:
#         logger.exception("Не удалось получить список программ: {}", e)
#         await message.answer("⚠️ Произошла ошибка при получении списка программ. Попробуйте позже.")
#         return

#     active_programs = [p for p in programs if p.get("is_active")]

#     if not active_programs:
#         await message.answer("📋 <b>Нет доступных программ обучения.</b>", parse_mode="HTML")
#         return

#     lines = [
#         f"• {p.get('name', 'Без названия')} ({p.get('min_age', '?')}–{p.get('max_age', '?')} лет)"
#         for p in active_programs
#     ]
#     text = "📋 <b>Наши программы обучения:</b>\n\n" + "\n".join(lines)

#     await message.answer(text, parse_mode="HTML")
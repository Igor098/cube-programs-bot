# from datetime import datetime, timedelta, timezone
# from aiogram import Router
# from aiogram.types import Message
# from aiogram.filters import Command
# from loguru import logger

# from tokens import AccessTokenData, get_token, user_tokens
# from services.auth_service import login


# router = Router()


# @router.message(Command("login"))
# async def handle_login(message: Message):
#     telegram_id = message.from_user.id
#     logger.info(f"Команда входа: {telegram_id}")
#     credentials = await login(telegram_id=telegram_id)
#     if credentials:
#         expires = datetime.now(timezone.utc) + timedelta(seconds=credentials.get("expires_in"))
        
#         user_tokens[telegram_id] = AccessTokenData(
#             access_token=credentials.get("access_token"),
#             expires_at=expires
#         )
#         await message.answer("Вы успешно вошли в систему.")
#     else:
#         await message.answer("Вы не являетесь администратором.")


# @router.message(Command("profile"))
# async def handle_profile(message: Message):
#     telegram_id = message.from_user.id
#     token = get_token(telegram_id)
#     if token:
#         await message.answer(f"Ваш токен: {token}")
#     else:
#         await message.answer("Вы не вошли в систему.")

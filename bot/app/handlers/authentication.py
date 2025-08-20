from datetime import datetime, timedelta, timezone
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from loguru import logger

from keyboards.main import main_keyboard
from tokens import AccessTokenData, get_token, user_tokens
from services.auth_service import login, profile as get_profile


router = Router()


@router.message(Command("login"))
async def handle_login(message: Message):
    telegram_id = message.from_user.id
    credentials = await login(telegram_id=telegram_id)
    if credentials:
        expires = datetime.now(timezone.utc) + timedelta(seconds=credentials.get("expires_in"))
        
        user_tokens[telegram_id] = AccessTokenData(
            access_token=credentials.get("access_token"),
            expires_at=expires
        )
        logger.info(f"Вход выполнен: {telegram_id}")
        await message.answer("Вы успешно вошли в систему.", reply_markup=main_keyboard(is_admin=True))
    else:
        await message.answer("Вы не являетесь администратором.", reply_markup=main_keyboard())
        
    try:
        await message.delete()
    except Exception as e:
        logger.error(f"Не удалось удалить сообщение. Ошибка: {e}")
        pass


@router.message(Command("profile"))
async def handle_profile(message: Message):
    telegram_id = message.from_user.id
    token = get_token(telegram_id)
    if not token:
        await message.answer("Вы не авторизованы в системе или закончилось время авторизации. Для повторной авторизации используйте команду: /login", parse_mode="HTML")
        try:
            await message.delete()
        except Exception as e:
            logger.error(f"Не удалось удалить сообщение. Ошибка: {e}")
            pass
        return
    
    is_admin = True if token else False
    
    profile = await get_profile(token=token)
    await message.answer(f"🪪 <b>Профиль пользователя:</b> \n\n        Имя: {profile.get("username")}", parse_mode="HTML", reply_markup=main_keyboard(is_admin))
    try:
        await message.delete()
    except Exception as e:
        logger.error(f"Не удалось удалить сообщение. Ошибка: {e}")
        pass

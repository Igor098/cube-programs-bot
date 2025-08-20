import asyncio
from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from services.programs_sync import sync_programs_from_api
from config import settings
from loguru import logger
from handlers import common_router, programs_router, authentication_router
from states.programs_store import store


async def on_startup(bot: Bot):
    logger.info("Старт бота: синхронизация каталога программ...")
    try:
        count, msg = await sync_programs_from_api()
        logger.info(f"Результат синхронизации: {msg}")
    except Exception as e:
        logger.exception(f"Ошибка при первичной загрузке каталога: {e}")


async def main():
    dp = Dispatcher()
    dp.startup.register(on_startup)
    dp.include_routers(common_router, programs_router, authentication_router)

    token = settings.TOKEN
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode='HTML'))
    logger.info("Бот запущен...")

    await dp.start_polling(bot, skip_updates=False, store=store)


if __name__ == "__main__":
    asyncio.run(main())

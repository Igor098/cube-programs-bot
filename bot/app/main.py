import asyncio
from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from config import settings
from loguru import logger
from handlers import common_router

dp = Dispatcher()
dp.include_router(common_router)


async def main():
    token = settings.TOKEN
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode='HTML'))
    logger.info("Starting bot...")
    
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())

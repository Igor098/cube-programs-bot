

from typing import Optional
from aiohttp import ClientSession, ClientConnectionError, ClientResponseError, ClientPayloadError, TooManyRedirects, InvalidURL, ClientConnectorError
from loguru import logger

from app.utils.decorators import with_aiohttp_session


@with_aiohttp_session
async def login(session: ClientSession, telegram_id: int) -> Optional[dict]:
    """
    Выполняет вход пользователя через API.
    :param session: HTTP сессия для выполнения запроса.
    :param telegram_id: ID пользователя в Telegram.
    """
    try:
        logger.info(f"Пользователь {telegram_id} пытается войти в систему")
        async with session.post("bot/admin/login", params={"telegram_id": telegram_id}) as response:
            response.raise_for_status()
            logger.info(f"Пользователь {telegram_id} вошел в систему")
            return await response.json()
    except ClientConnectorError:
        logger.error("Не удалось подключиться к серверу")
    except ClientConnectionError as e:
        logger.error(f"Ошибка соединения: {e}")
    except TooManyRedirects as e:
        logger.error(f"Слишком много перенаправлений: {e}")
    except ClientResponseError as e:
        logger.error(f"Ошибка ответа сервера: {e}")
    except ClientPayloadError as e:
        logger.error(f"Ошибка чтения тела ответа: {e}")
    except TimeoutError as e:
        logger.error(f"Превышено время ожидания: {e}")
    except InvalidURL as e:
        logger.error(f"Неверный URL: {e}")
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")
    finally:
        await session.close()

@with_aiohttp_session
async def profile(session: ClientSession, token: str) -> Optional[dict]:
    """
    Получает информацию о профиле пользователя через API.
    :param session: HTTP сессия для выполнения запроса.
    :param token: Токен доступа пользователя.
    """
    try:
        async with session.get(f"bot/admin/me", headers={"Authorization": f"Bearer {token}"}) as response:
            response.raise_for_status()
            return await response.json()
    except ClientConnectorError:
        logger.error("Не удалось подключиться к серверу")
    except ClientConnectionError as e:
        logger.error(f"Ошибка соединения: {e}")
    except TooManyRedirects as e:
        logger.error(f"Слишком много перенаправлений: {e}")
    except ClientResponseError as e:
        logger.error(f"Ошибка ответа сервера: {e}")
    except ClientPayloadError as e:
        logger.error(f"Ошибка чтения тела ответа: {e}")
    except TimeoutError as e:
        logger.error(f"Превышено время ожидания: {e}")
    except InvalidURL as e:
        logger.error(f"Неверный URL: {e}")
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")
    finally:
        await session.close()

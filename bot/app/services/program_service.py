from loguru import logger
from aiohttp import ClientSession, ClientConnectionError, ClientResponseError, ClientPayloadError, TooManyRedirects, InvalidURL, ClientConnectorError
from asyncio import TimeoutError

from app.utils.decorators import with_aiohttp_session

@with_aiohttp_session
async def get_programs_list(session: ClientSession) -> list[dict[str, str]]:
    """
    Запрашивает список программ из API.
    :param session: HTTP сессия для выполнения запроса.
    """
    try:
        async with session.get("programs") as response:
            logger.info(f"Программы: {response}")
            response.raise_for_status()
            return await response.json()
    except ClientConnectorError as e:
        logger.error(f"Не удалось подключиться к серверу. Ошибка: {e}")
        return []
    except ClientConnectionError as e:
        logger.error(f"Ошибка соединения: {e}")
        return []
    except TooManyRedirects as e:
        logger.error(f"Слишком много перенаправлений: {e}")
        return []
    except ClientResponseError as e:
        logger.error(f"Ошибка ответа сервера: {e}")
        return []
    except ClientPayloadError as e:
        logger.error(f"Ошибка чтения тела ответа: {e}")
        return []
    except TimeoutError as e:
        logger.error(f"Превышено время ожидания: {e}")
        return []
    except InvalidURL as e:
        logger.error(f"Неверный URL: {e}")
        return []
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")
        return []
    finally:
        await session.close()
    
    
@with_aiohttp_session
async def add_program(session: ClientSession, token: str, program_data: dict) -> None:
    """
    Добавляет новую программу через API.
    :param session: HTTP сессия для выполнения запроса.
    :param token: Токен доступа пользователя.
    :param program_data: Данные программы для добавления.
    """
    try:
        logger.info(f"Добавление программы: {program_data}")
        async with session.post("bot/program", headers={"Authorization": f"Bearer {token}"}, json=program_data) as response:
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

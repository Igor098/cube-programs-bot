from aiohttp import ClientConnectionError, ClientConnectorError, ClientPayloadError, ClientResponseError, ClientSession, InvalidURL, TooManyRedirects
from loguru import logger
from utils.decorators import with_aiohttp_session
from aiogram.types import BufferedInputFile

@with_aiohttp_session
async def get_enroll_blank(session: ClientSession) -> list[dict[str, str]]:
    """
    Запрашивает список программ из API.
    :param session: HTTP сессия для выполнения запроса.
    """
    try:
        async with session.get("files/enroll-form") as response:
            response.raise_for_status()
            data = await response.read()
            
            cd = response.headers.get("Content-Disposition", "")
            filename = "enroll_form.pdf"
            if "filename=" in cd:
                filename = cd.split("filename=")[-1].strip().strip('"')

            return BufferedInputFile(data, filename=filename)
    except ClientConnectorError:
        logger.error("Не удалось подключиться к серверу")
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
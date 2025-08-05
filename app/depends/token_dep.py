from fastapi.params import Depends
from fastapi.requests import Request
from loguru import logger
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.error_messages import TOKEN_NOT_FOUND, TOKEN_NOT_VALID, CSRF_NOT_FOUND, CSRF_NOT_VALID
from app.core.security import decode_token
from app.core.token_types import TokenType
from app.depends.redis_dep import get_redis
from app.depends.session_dep import get_session_with_commit
from app.exceptions.business import TokenNotFoundError
from app.exceptions.http import UnauthorizedException
from app.models.admin import Admin
from app.services.admin_service import AdminService


def get_admin_service(
        session: AsyncSession = Depends(get_session_with_commit)
) -> AdminService:
    return AdminService(session)


async def get_current_admin(
        request: Request,
        admin_service: AdminService = Depends(get_admin_service)
) -> Admin:
    """
    Получить текущего авторизованного администратора по access_token в cookie.
    :param request: запрос пользователя
    :param admin_service: сервис администраторов
    :return: текущий администратор
    """
    token = request.cookies.get(f"{TokenType.ACCESS}_token")

    if not token:
        raise UnauthorizedException(detail=TOKEN_NOT_FOUND)

    payload = decode_token(token, TokenType.ACCESS)
    admin_id = payload.get("sub")

    if not admin_id:
        raise UnauthorizedException(detail=TOKEN_NOT_VALID)

    admin = await admin_service.get_admin_by_id(admin_id)
    return admin


async def get_current_bot_admin(
        request: Request,
        redis: Redis = Depends(get_redis),
        admin_service: AdminService = Depends(get_admin_service)
) -> Admin:
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise UnauthorizedException(detail=TOKEN_NOT_FOUND)

    token = auth_header.removeprefix("Bearer ").strip()
    payload = decode_token(token, TokenType.BOT)
    telegram_id = payload.get("sub")

    if not telegram_id:
        raise UnauthorizedException(detail=TOKEN_NOT_VALID)

    redis_key = f"bot:admin:{telegram_id}"
    stored_token = await redis.get(redis_key)
    if not stored_token or stored_token != token:
        raise UnauthorizedException(detail=TOKEN_NOT_VALID)

    admin = await admin_service.get_admin_by_telegram_id(telegram_id)
    return admin


async def validate_csrf_token(
        request: Request,
        redis: Redis = Depends(get_redis)
) -> None:
    """
    Проверить валидность csrf токена
    :param request: запрос пользователя
    :param redis: клиент redis
    :return: None
    """
    csrf = request.cookies.get(f"{TokenType.CSRF}_token")
    access_token = request.cookies.get(f"{TokenType.ACCESS}_token")
    header_csrf = request.headers.get("X-CSRF-Token")

    if not access_token or not csrf or not header_csrf:
        raise TokenNotFoundError(CSRF_NOT_FOUND)

    if csrf != header_csrf:
        raise UnauthorizedException(detail=CSRF_NOT_VALID)

    payload = decode_token(access_token, TokenType.ACCESS)
    admin_id = payload.get("sub")
    if not admin_id:
        raise UnauthorizedException(detail=TOKEN_NOT_VALID)

    redis_csrf = await redis.get(f"admin:csrf:{admin_id}")
    if not redis_csrf:
        raise TokenNotFoundError(CSRF_NOT_FOUND)

    if redis_csrf != header_csrf:
        raise UnauthorizedException(detail=CSRF_NOT_VALID)

    logger.info(f"CSRF для admin {admin_id} успешно пройден")

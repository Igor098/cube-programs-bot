from datetime import timedelta

from fastapi.responses import Response
from fastapi.requests import Request
from redis import RedisError
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.error_messages import ADMIN_NOT_FOUND, ADMIN_ALREADY_EXISTS, ADMIN_TELEGRAM_ID_ALREADY_EXISTS, \
    INCORRECT_CREDENTIALS, TOKEN_NOT_VALID
from core.security import create_bot_token, hash_element, verify, create_access_token, create_refresh_token, \
    create_csrf_token, set_cookie, decode_token
from core.token_types import TokenType
from crud.admin import AdminDAO
from exceptions.business import ConflictError, NotFoundError, UnauthorizedError, TokenNotValidError
from models.admin import Admin
from schemas.admin import AdminFilter, AdminCreateSchema, AdminLoginSchema
from loguru import logger


class AdminService:
    def __init__(self, session: AsyncSession):
        self._admin_dao = AdminDAO(session)

    async def get_admin_by_id(self, admin_id: int) -> Admin:
        admin = await self._admin_dao.find_one_or_none_by_id(admin_id)
        if not admin:
            logger.warning(f"Администратор с id: {admin_id} не найден")
            raise NotFoundError(ADMIN_NOT_FOUND)

        return admin

    async def get_admin_by_telegram_id(self, telegram_id: int) -> Admin:
        admin = await self._admin_dao.find_one_or_none(AdminFilter(telegram_id=telegram_id))
        if not admin:
            logger.warning(f"Администратор с телеграм id: {telegram_id} не найден")
            raise NotFoundError(ADMIN_NOT_FOUND)

        return admin

    async def get_admin_by_username(self, username: str) -> Admin:
        admin = await self._admin_dao.find_one_or_none(AdminFilter(username=username))
        if not admin:
            logger.warning(f"Администратор с именем: {username} не найден")
            raise NotFoundError(ADMIN_NOT_FOUND)
        return admin

    async def get_bot_admin(self, request: Request, redis: Redis) -> Admin:
        try:
            token = request.headers.get("Authorization")
            if not token or not token.startswith("Bearer "):
                raise UnauthorizedError(TOKEN_NOT_VALID)

            token = token.removeprefix("Bearer ").strip()
            payload = decode_token(token, TokenType.BOT)

            telegram_id = payload.get("sub")
            if not telegram_id:
                raise UnauthorizedError(TOKEN_NOT_VALID)

            redis_key = f"bot:admin:{telegram_id}"
            stored_token = await redis.get(redis_key)
            if not stored_token or stored_token != token:
                raise UnauthorizedError(TOKEN_NOT_VALID)

            admin = await self.get_admin_by_telegram_id(telegram_id)
            return admin

        except NotFoundError:
            raise UnauthorizedError(TOKEN_NOT_VALID)

        except UnauthorizedError as e:
            raise UnauthorizedError(str(e))

        except RedisError as e:
            logger.error(f"Ошибка при взаимодействии с Redis: {e}")
            raise RedisError(str(e))

        except TokenNotValidError as e:
            raise TokenNotValidError(str(e))

    async def create_admin(self, admin: AdminCreateSchema) -> Admin:
        is_exists = await self._admin_dao.find_one_or_none(AdminFilter(username=admin.username))
        if is_exists:
            logger.warning(f"Администратор с именем: {admin.username} уже существует")
            raise ConflictError(ADMIN_ALREADY_EXISTS)

        if admin.telegram_id:
            is_exists = await self._admin_dao.find_one_or_none(AdminFilter(telegram_id=admin.telegram_id))
            if is_exists:
                logger.warning(f"Администратор с телеграм id: {admin.telegram_id} уже существует")
                raise ConflictError(ADMIN_TELEGRAM_ID_ALREADY_EXISTS)

        password_hash = hash_element(admin.password)
        admin.password = password_hash

        return await self._admin_dao.add(admin)

    async def delete_admin(self, admin_id: int) -> dict:
        await self.get_admin_by_id(admin_id)
        await self._admin_dao.delete(AdminFilter(id=admin_id))

        return {"message": "Администратор удален"}

    async def login(self, response: Response, redis: Redis, user_data: AdminLoginSchema) -> Admin:
        try:
            username = user_data.username
            password = user_data.password

            admin = await self.get_admin_by_username(username)
            is_correct_password = verify(password, admin.password)

            if not is_correct_password:
                logger.warning(f"Неверный пароль для администратора с именем: {username}")
                raise UnauthorizedError(INCORRECT_CREDENTIALS)

            access_token = create_access_token(admin.id)
            refresh_token, jti = create_refresh_token(admin.id)
            csrf_token = create_csrf_token(admin.id)

            await redis.set(f"admin:refresh:{admin.id}:{jti}", refresh_token, ex=timedelta(seconds=settings.REFRESH_TTL))
            await redis.set(f"admin:csrf:{admin.id}", csrf_token, ex=timedelta(seconds=settings.CSRF_TTL))

            set_cookie(response, access_token, TokenType.ACCESS, settings.ACCESS_TTL)
            set_cookie(response, refresh_token, TokenType.REFRESH, settings.REFRESH_TTL)
            set_cookie(response, csrf_token, TokenType.CSRF, settings.CSRF_TTL)

            logger.info(f"Администратор с именем: {username} вошел в систему")

            return admin

        except NotFoundError as e:
            raise NotFoundError(str(e))

        except UnauthorizedError as e:
            raise UnauthorizedError(str(e))

        except RedisError as e:
            logger.error(f"Ошибка при взаимодействии с Redis: {e}")
            raise RedisError(str(e))

    async def refresh_tokens(self, request: Request, response: Response, redis: Redis) -> Admin:
        try:
            refresh_token = request.cookies.get(f"{TokenType.REFRESH}_token")
            payload = decode_token(refresh_token, TokenType.REFRESH)
            admin_id = payload.get("sub")
            jti = payload.get("jti")
            if not admin_id or not jti:
                logger.warning("Некорректный refresh_token")
                raise UnauthorizedError(TOKEN_NOT_VALID)

            redis_key = f"admin:refresh:{admin_id}:{jti}"
            exists = await redis.get(redis_key)
            if not exists:
                logger.warning(f"Токен обновления не найден или отозван")
                raise UnauthorizedError(TOKEN_NOT_VALID)

            admin = await self.get_admin_by_id(admin_id)
            access_token = create_access_token(admin.id)
            refresh_token, jti = create_refresh_token(admin.id)
            csrf_token = create_csrf_token(admin.id)

            await redis.set(f"admin:refresh:{admin.id}:{jti}", refresh_token, ex=timedelta(seconds=settings.REFRESH_TTL))
            await redis.set(f"admin:csrf:{admin.id}", csrf_token, ex=timedelta(seconds=settings.CSRF_TTL))

            await redis.delete(redis_key)

            set_cookie(response, access_token, TokenType.ACCESS, settings.ACCESS_TOKEN_TTL)
            set_cookie(response, refresh_token, TokenType.REFRESH, settings.REFRESH_TOKEN_TTL)
            set_cookie(response, csrf_token, TokenType.CSRF, settings.CSRF_TOKEN_TTL)

            logger.info(f"Администратор с идентификатором: {admin.id} обновил токены")

            return admin

        except NotFoundError as e:
            raise NotFoundError(str(e))

        except RedisError as e:
            logger.error(f"Ошибка при взаимодействии с Redis: {e}")
            raise RedisError(str(e))

        except UnauthorizedError as e:
            raise UnauthorizedError(str(e))

        except TokenNotValidError as e:
            raise TokenNotValidError(str(e))

    async def logout(self, request: Request, response: Response, redis: Redis) -> dict:
        try:
            refresh_token = request.cookies.get(f"{TokenType.REFRESH}_token")
            if not refresh_token:
                logger.warning("refresh_token отсутствует")
                return {"detail": "Нет refresh_token — уже разлогинен"}

            payload = decode_token(refresh_token, TokenType.REFRESH)
            admin_id = payload.get("sub")
            admin = await self.get_admin_by_id(admin_id)
            jti = payload.get("jti")
            if not admin_id or not jti or not admin:
                logger.warning("Некорректный refresh_token")
                raise UnauthorizedError(TOKEN_NOT_VALID)

            redis_key = f"admin:refresh:{admin_id}:{jti}"
            await redis.delete(redis_key)
            response.delete_cookie(f"{TokenType.ACCESS}_token")
            response.delete_cookie(f"{TokenType.REFRESH}_token")
            response.delete_cookie(f"{TokenType.CSRF}_token")
            logger.info(f"Администратор с идентификатором: {admin_id} вышел из системы")

            return {"detail": "Вы успешно вышли из системы"}

        except NotFoundError as e:
            raise NotFoundError(str(e))

        except RedisError as e:
            logger.error(f"Ошибка при взаимодействии с Redis: {e}")
            raise RedisError(str(e))

        except UnauthorizedError as e:
            raise UnauthorizedError(str(e))

        except TokenNotValidError as e:
            raise TokenNotValidError(str(e))

    async def bot_login(self, redis: Redis, telegram_id: int) -> str:
        try:
            await self.get_admin_by_telegram_id(telegram_id)

            token = create_bot_token(telegram_id)

            await redis.set(f"bot:admin:{telegram_id}", token, ex=timedelta(seconds=settings.BOT_TTL))
            logger.info(f"Администратор с телеграм id: {telegram_id} вошел в бота")

            return token

        except NotFoundError as e:
            logger.warning(f"Администратор с телеграм id: {telegram_id} не найден")
            raise NotFoundError(str(e))

        except RedisError as e:
            logger.error(f"Ошибка при взаимодействии с Redis: {e}")
            raise RedisError(str(e))

    @staticmethod
    async def bot_logout(redis: Redis, telegram_id: int) -> dict:
        try:
            await redis.delete(f"bot:admin:{telegram_id}")
            logger.info(f"Администратор с телеграм id: {telegram_id} вышел из бота")
            return {"detail": "Вы успешно вышли из своего аккаунта"}
        except RedisError as e:
            logger.error(f"Ошибка при взаимодействии с Redis: {e}")
            raise RedisError(str(e))
from fastapi import APIRouter, Depends, Security
from fastapi.requests import Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.token_types import TokenType
from app.depends.redis_dep import get_redis
from app.depends.session_dep import get_session_with_commit
from app.depends.token_dep import get_current_bot_admin
from app.exceptions.business import ConflictError, NotFoundError
from app.exceptions.http import ConflictException, NotFoundException
from app.models import Admin
from app.schemas.admin import AdminCreateSchema, AdminTelegramSchema, AdminSchema
from app.services.admin_service import AdminService

router = APIRouter(prefix="/v1/bot/admin", tags=["Администрирование через бота"])

bearer_scheme = HTTPBearer()


def get_admin_service(session: AsyncSession = Depends(get_session_with_commit)) -> AdminService:
    return AdminService(session)


@router.get("/me", response_model=AdminSchema)
async def get_me(
        request: Request,
        redis: Redis = Depends(get_redis),
        admin_service: AdminService = Depends(get_admin_service),
        authorized_admin: Admin = Depends(get_current_bot_admin),
        credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)

) -> AdminSchema:
    admin = await admin_service.get_bot_admin(request, redis)
    return AdminSchema.model_validate(admin, from_attributes=True)


@router.post("/register", response_model=AdminSchema)
async def register(
        admin: AdminCreateSchema,
        admin_service: AdminService = Depends(get_admin_service),
        authorized_admin: Admin = Depends(get_current_bot_admin),
        credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
) -> AdminSchema:
    try:
        admin = await admin_service.create_admin(admin)
        return AdminSchema.model_validate(admin)
    except ConflictError as e:
        raise ConflictException(detail=str(e))


@router.post("/login")
async def login(
        telegram_id: int,
        redis: Redis = Depends(get_redis),
        admin_service: AdminService = Depends(get_admin_service)
) -> AdminTelegramSchema:
    try:
        await admin_service.get_admin_by_telegram_id(telegram_id)
        token = await admin_service.bot_login(redis, telegram_id)

        return AdminTelegramSchema(access_token=token, token_type=TokenType.BOT, expires_in=settings.BOT_TTL)
    except NotFoundError as e:
        raise NotFoundException(detail=str(e))


@router.post("/logout")
async def logout(
        telegram_id: int,
        redis: Redis = Depends(get_redis),
        admin_service: AdminService = Depends(get_admin_service),
        authorized_admin: Admin = Depends(get_current_bot_admin),
        credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
) -> dict:
    try:
        await admin_service.get_admin_by_telegram_id(telegram_id)
        return await admin_service.bot_logout(redis, telegram_id)
    except NotFoundError as e:
        raise NotFoundException(detail=str(e))


@router.delete("/delete")
async def delete(
        telegram_id: int,
        admin_service: AdminService = Depends(get_admin_service),
        authorized_admin: Admin = Depends(get_current_bot_admin),
        credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
) -> dict:
    try:
        return await admin_service.delete_admin(telegram_id)
    except NotFoundError as e:
        raise NotFoundException(detail=str(e))

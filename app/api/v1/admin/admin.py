from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.depends.redis_dep import get_redis
from app.depends.session_dep import get_session_with_commit
from app.depends.token_dep import get_current_admin
from app.exceptions.business import NotFoundError, ConflictError
from app.exceptions.http import NotFoundException, ConflictException
from app.models.admin import Admin
from app.schemas.admin import AdminCreateSchema, AdminSchema, AdminLoginSchema
from app.services.admin_service import AdminService
from fastapi.responses import Response
from fastapi.requests import Request

router = APIRouter(prefix="/v1/admin", tags=["Администраторы"])


def get_admin_service(session: AsyncSession = Depends(get_session_with_commit)) -> AdminService:
    return AdminService(session)


@router.get("/{admin_id}", response_model=AdminSchema)
async def get_admin_by_id(
        admin_id: int,
        admin_service: AdminService = Depends(get_admin_service),
        authorized_admin: Admin = Depends(get_current_admin)
) -> AdminSchema:
    try:
        admin = await admin_service.get_admin_by_id(admin_id)
        return AdminSchema.model_validate(admin, from_attributes=True)
    except NotFoundError as e:
        raise NotFoundException(detail=str(e))
    except Exception as e:
        raise e


@router.get("/username/{username}", response_model=AdminSchema)
async def get_admin_by_username(
        username: str,
        admin_service: AdminService = Depends(get_admin_service),
        authorized_admin: Admin = Depends(get_current_admin)
) -> AdminSchema:
    try:
        admin = await admin_service.get_admin_by_username(username)
        return AdminSchema.model_validate(admin, from_attributes=True)
    except NotFoundError as e:
        raise NotFoundException(detail=str(e))
    except Exception as e:
        raise e


@router.get("/telegram_id/{telegram_id}", response_model=AdminSchema)
async def get_admin_by_telegram_id(
        telegram_id: int,
        admin_service: AdminService = Depends(get_admin_service),
        authorized_admin: Admin = Depends(get_current_admin)
) -> AdminSchema:
    try:
        admin = await admin_service.get_admin_by_telegram_id(telegram_id)
        return AdminSchema.model_validate(admin, from_attributes=True)
    except NotFoundError as e:
        raise NotFoundException(detail=str(e))
    except Exception as e:
        raise e


@router.post("/", response_model=AdminSchema)
async def create_admin(
        admin_data: AdminCreateSchema,
        admin_service: AdminService = Depends(get_admin_service),
        authorized_admin: Admin = Depends(get_current_admin)
) -> AdminSchema:
    try:
        admin = await admin_service.create_admin(admin_data)
        return AdminSchema.model_validate(admin, from_attributes=True)
    except ConflictError as e:
        raise ConflictException(detail=str(e))
    except Exception as e:
        raise e


@router.post("/login")
async def login(
        user_data: AdminLoginSchema,
        response: Response,
        redis: Redis = Depends(get_redis),
        admin_service: AdminService = Depends(get_admin_service)
) -> AdminSchema:
    try:
        admin = await admin_service.login(response, redis, user_data)
        return AdminSchema.model_validate(admin, from_attributes=True)
    except NotFoundError as e:
        raise NotFoundException(detail=str(e))
    except Exception as e:
        raise e


@router.post("/logout")
async def logout(
        request: Request,
        response: Response,
        redis: Redis = Depends(get_redis),
        admin_service: AdminService = Depends(get_admin_service)
) -> dict:
    try:
        return await admin_service.logout(request, response, redis)
    except NotFoundError as e:
        raise NotFoundException(detail=str(e))
    except Exception as e:
        raise e


@router.delete("/{admin_id}")
async def delete_admin(
        admin_id: int,
        admin_service: AdminService = Depends(get_admin_service),
        authorized_admin: Admin = Depends(get_current_admin)
) -> dict:
    try:
        return await admin_service.delete_admin(admin_id)
    except NotFoundError as e:
        raise NotFoundException(detail=str(e))
    except Exception as e:
        raise e

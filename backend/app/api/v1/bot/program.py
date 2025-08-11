from fastapi import APIRouter, Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession

from depends.session_dep import get_session_with_commit
from depends.token_dep import get_current_bot_admin
from exceptions.business import ConflictError, NotFoundError
from exceptions.http import ConflictException, NotFoundException
from models.admin import Admin
from schemas.program import ProgramCreateSchema, ProgramUpdateSchema
from services.program_service import ProgramService
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

bearer_scheme = HTTPBearer()

router = APIRouter(prefix="/v1/bot/program", tags=["Программы через бота"])


def get_program_service(session: AsyncSession = Depends(get_session_with_commit)) -> ProgramService:
    return ProgramService(session)


@router.post("/",)
async def create_program(
        program: ProgramCreateSchema,
        program_service: ProgramService = Depends(get_program_service),
        authorized_admin: Admin = Depends(get_current_bot_admin),
        credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
):
    try:
        return await program_service.create_program(program)
    except ConflictError as e:
        raise ConflictException(detail=str(e))


@router.put("/{program_id}")
async def update_program(
        program_id: int,
        program: ProgramUpdateSchema,
        program_service: ProgramService = Depends(get_program_service),
        authorized_admin: Admin = Depends(get_current_bot_admin),
        credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
):
    try:
        return await program_service.update_program(program_id, program)
    except NotFoundError as e:
        raise NotFoundException(detail=str(e))


@router.patch("/{program_id}")
async def partial_update_program(
        program_id: int,
        program: ProgramUpdateSchema,
        program_service: ProgramService = Depends(get_program_service),
        authorized_admin: Admin = Depends(get_current_bot_admin),
        credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
):
    try:
        return await program_service.update_program(program_id, program)
    except NotFoundError as e:
        raise NotFoundException(detail=str(e))


@router.delete("/{program_id}")
async def delete_program(
        program_id: int,
        program_service: ProgramService = Depends(get_program_service),
        authorized_admin: Admin = Depends(get_current_bot_admin),
        credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
):
    try:
        return await program_service.delete_program(program_id)
    except NotFoundError as e:
        raise NotFoundException(detail=str(e))

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from depends.session_dep import get_session_with_commit
from exceptions.business import NotFoundError
from exceptions.http import NotFoundException
from schemas.program import ProgramSchema
from services.program_service import ProgramService

router = APIRouter(prefix="/v1", tags=["Программы"])


def get_program_service(session: AsyncSession = Depends(get_session_with_commit)) -> ProgramService:
    return ProgramService(session)


@router.get("/programs", response_model=List[ProgramSchema])
async def get_programs(
        program_service: ProgramService = Depends(get_program_service)
) -> List[ProgramSchema]:
    try:
        return await program_service.get_programs()
    except NotFoundError as e:
        raise NotFoundException(detail=str(e))


@router.get("/program/{program_id}", response_model=ProgramSchema)
async def get_program_by_id(
        program_id: int,
        program_service: ProgramService = Depends(get_program_service)
) -> ProgramSchema:
    try:
        program = await program_service.get_program_by_id(program_id)
        return ProgramSchema.model_validate(program, from_attributes=True)
    except NotFoundError as e:
        raise NotFoundException(detail=str(e))


@router.get("/program/name/{name}", response_model=ProgramSchema)
async def get_program_by_name(
        name: str,
        program_service: ProgramService = Depends(get_program_service)
) -> ProgramSchema:
    try:
        program = await program_service.get_program_by_name(name)
        return ProgramSchema.model_validate(program, from_attributes=True)
    except NotFoundError as e:
        raise NotFoundException(detail=str(e))

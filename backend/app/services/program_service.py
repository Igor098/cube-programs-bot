from sqlalchemy.ext.asyncio import AsyncSession

from core.error_messages import PROGRAM_ALREADY_EXISTS, PROGRAM_NOT_FOUND
from crud.program import ProgramDAO
from exceptions.business import NotFoundError, ConflictError
from schemas.program import ProgramCreateSchema, ProgramFilter, ProgramUpdateSchema
from loguru import logger


class ProgramService:
    def __init__(self, session: AsyncSession):
        self._program_dao = ProgramDAO(session)

    async def get_programs(self):
        programs = await self._program_dao.find_all()
        if not programs:
            logger.warning("Программы не найдены")
            raise NotFoundError(PROGRAM_NOT_FOUND)

        return programs

    async def get_program_by_id(self, program_id: int):
        program = await self._program_dao.find_one_or_none_by_id(program_id)
        if not program:
            logger.warning(f"Программа с id: {program_id} не найдена")
            raise NotFoundError(PROGRAM_NOT_FOUND)

        return program

    async def get_program_by_name(self, name: str):
        program = await self._program_dao.find_one_or_none(ProgramFilter(name=name))
        if not program:
            logger.warning(f"Программа с названием: {name} не найдена")
            raise NotFoundError(PROGRAM_NOT_FOUND)

        return program

    async def create_program(self, program: ProgramCreateSchema):
        is_exists = await self._program_dao.find_one_or_none(ProgramFilter(name=program.name))
        if is_exists:
            logger.warning(f"Программа с названием: {program.name} уже существует")
            raise ConflictError(PROGRAM_ALREADY_EXISTS)

        return await self._program_dao.add(program)

    async def update_program(self, program_id: int, program: ProgramUpdateSchema):
        await self.get_program_by_id(program_id)

        return await self._program_dao.update(ProgramFilter(id=program_id), program)

    async def delete_program(self, program_id: int):
        await self.get_program_by_id(program_id)

        return await self._program_dao.delete(ProgramFilter(id=program_id))

    async def enable_program(self, program_id: int):
        await self.get_program_by_id(program_id)

        return await self._program_dao.update(ProgramFilter(id=program_id), ProgramUpdateSchema(is_active=True))

    async def disable_program(self, program_id: int):
        await self.get_program_by_id(program_id)

        return await self._program_dao.update(ProgramFilter(id=program_id), ProgramUpdateSchema(is_active=False))

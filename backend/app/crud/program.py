from typing import List

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from loguru import logger

from models.group import Group
from crud.base import BaseDAO
from models.program import Program


class ProgramDAO(BaseDAO):
    model = Program
    
    async def get_programs(self) -> List[Program]:
        try:
            logger.info("Поиск всех программ")
            stmt = (
            select(Program)
            .options(
                selectinload(Program.groups)
                .selectinload(Group.time_slots)
            )
            .order_by(Program.name.asc())
        )
            result = await self._session.execute(stmt)
            records = result.scalars().all()
            logger.info(f"Найдено {len(records)} программ")
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех программ: {e}")
            raise
    
    async def get_program_by_id(self, program_id: int) -> Program:
        try:
            stmt = (
                select(Program)
                .filter_by(id=program_id)
                .options(
                    selectinload(Program.groups)
                    .selectinload(Group.time_slots)
                )
                .order_by(Program.name.asc())
            )
            result = await self._session.execute(stmt)
            log_message = f"Запись {'найдена' if result else 'не найдена'} с id: {program_id}"
            logger.info(log_message)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи с id: {program_id}: {e}")
            raise
        
    async def get_program_by_name(self, program_name: str) -> Program:
        try:
            stmt = (
                select(Program)
                .filter_by(name=program_name)
                .options(
                    selectinload(Program.groups)
                    .selectinload(Group.time_slots)
                )
                .order_by(Program.name.asc())
            )
            result = await self._session.execute(stmt)
            log_message = f"Запись {'найдена' if result else 'не найдена'} с именем: {program_name}"
            logger.info(log_message)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи с именем: {program_name}: {e}")
            raise
        
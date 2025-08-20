from loguru import logger
from app.exceptions.http import NotFoundException
from app.crud.group import GroupDAO
from app.core.error_messages import GROUP_NOT_FOUND

class GroupService:
    def __init__(self, session):
        self.group_dao = GroupDAO(session)
        
    async def get_groups(self):
        groups = await self.group_dao.find_all()
        if not groups:
            logger.warning("Группы не найдены")
            return []

        return groups
    
    async def get_group_by_id(self, group_id: int):
        group = await self.group_dao.find_one_or_none_by_id(group_id)
        if not group:
            logger.warning(f"Группа с id: {group_id} не найдена")
            raise NotFoundException(detail=GROUP_NOT_FOUND)

        return group
    
    async def get_group_by_name(self, name: str):
        group = await self.group_dao.find_one_or_none(GroupFilter(name=name))
        if not group:
            logger.warning(f"Группа с названием: {name} не найдена")
            raise NotFoundException(detail=GROUP_NOT_FOUND)

        return group
    
    
        
        
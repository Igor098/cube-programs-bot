from app.models.group import Group
from .base import BaseDAO


class GroupDAO(BaseDAO):
    model = Group
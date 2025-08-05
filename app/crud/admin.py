from app.crud.base import BaseDAO
from app.models.admin import Admin


class AdminDAO(BaseDAO):
    model = Admin

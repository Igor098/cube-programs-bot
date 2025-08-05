from app.crud.base import BaseDAO
from app.models.program import Program


class ProgramDAO(BaseDAO):
    model = Program

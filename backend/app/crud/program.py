from crud.base import BaseDAO
from models.program import Program


class ProgramDAO(BaseDAO):
    model = Program

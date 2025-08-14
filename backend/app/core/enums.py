from enum import Enum


class ProgramLevel(str, Enum):
    START = "старт"
    BASE = "база"
    ADVANCED = "про"
    
    def __str__(self):
        return self.value

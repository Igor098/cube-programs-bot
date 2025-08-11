from enum import Enum


class ProgramLevel(str, Enum):
    START = "старт"
    BASE = "база"
    ADVANCED = "про"
    
    def __str__(self):
        return self.value


class ProgramCategory(str, Enum):
    DESIGN = "дизайн"
    PROGRAMMING = "программирование"
    ROBOTICS = "робототехника"
    DEVELOPMENT = "разработка"
    COMPUTER_SCIENCE = "информатика"
    COMPUTERS = "компьютеры"
    
    @property
    def label(self) -> str:
        return {
            "DESIGN": "дизайн",
            "PROGRAMMING": "программирование",
            "ROBOTICS": "робототехника",
            "DEVELOPMENT": "разработка",
            "COMPUTER_SCIENCE": "информатика",
            "COMPUTERS": "компьютеры",
        }[self.value]

    def __str__(self):
        return self.value

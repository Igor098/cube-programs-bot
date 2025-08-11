from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class Program:
    name: str
    short_name: str
    description: str
    min_age: int
    max_age: int
    category: str
    program_level: Optional[str]
    navigator_link: str
    requirements: Optional[str]
    image_url: Optional[str]
    is_active: bool
    

@dataclass
class ProgramWithId(Program):
    id: int
    
from dataclasses import dataclass
from datetime import time
from typing import List, Optional


@dataclass
class TimeSlot:
    id: int
    weekday: int
    start_time: time
    end_time: time


@dataclass
class Group:
    id: int
    name: str
    time_slots: List[TimeSlot]


@dataclass
class Program:
    name: str
    short_name: str
    description: str
    min_age: int
    max_age: int
    program_level: Optional[str]
    navigator_link: str
    requirements: Optional[str]
    image_url: Optional[str]
    is_active: bool
    
    groups: List[Group]
    

@dataclass
class ProgramWithId(Program):
    id: int
    
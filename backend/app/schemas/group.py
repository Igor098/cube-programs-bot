from typing import List
from pydantic import BaseModel, Field, field_validator

from schemas.time_slot import TimeSlotSchema


class _GroupBaseValidator(BaseModel):
    @field_validator("name", mode="before", check_fields=False)
    @classmethod
    def _normalize_str(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            v = v.strip()
            v = " ".join(v.split())
            if v == "":
                return None
        return v

class GroupCreateSchema(_GroupBaseValidator):
    name: str = Field(..., min_length=1, max_length=16, title="Название группы", description="В этом поле содержится название группы", examples=["1ПП", "1ВБ", "1БПЛА"])
    program_id: int = Field(..., title="ID программы", description="В этом поле содержится ID программы", examples=[1, 2, 3])
    slot_ids: List[int] = Field(..., title="ID слотов", description="В этом поле содержится список ID слотов", examples=[[1, 2, 3], [12]])
    

class GroupSchema(BaseModel):
    id: int
    name: str
    time_slots: List[TimeSlotSchema]
    
    model_config = {
        "from_attributes": True
    }
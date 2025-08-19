from datetime import time
from pydantic import BaseModel, field_serializer


class TimeSlotSchema(BaseModel):
    id: int
    weekday: int
    start_time: time
    end_time: time
    
    model_config = {
        "from_attributes": True
    }

    @field_serializer("start_time", "end_time")
    def _to_str(self, v: time, _info):
        return v.isoformat(timespec="minutes")

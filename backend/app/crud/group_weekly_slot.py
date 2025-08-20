from app.models.time_slot import TimeSlot
from .base import BaseDAO


class GroupWeeklySlotDAO(BaseDAO):
    model = TimeSlot
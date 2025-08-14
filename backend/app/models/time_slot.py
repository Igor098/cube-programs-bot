from datetime import time
from typing import List

from sqlalchemy import CheckConstraint, SmallInteger, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.schema import ForeignKey

from database.base import Base

class TimeSlot(Base):
    __tablename__ = "time_slots"
    __table_args__ = (
        CheckConstraint("weekday BETWEEN 1 AND 7", name="chk_timeslot_weekday"),
        CheckConstraint("start_time < end_time", name="chk_timeslot_time_order"),
        UniqueConstraint("weekday", "start_time", "end_time", name="uq_timeslot_window"),
    )

    weekday: Mapped[int] = mapped_column(SmallInteger)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)

    group_links: Mapped[List["GroupTimeSlot"]] = relationship(
        back_populates="time_slot",
        lazy="raise",
    )
    
    groups: Mapped[List["Group"]] = relationship(
        secondary="group_time_slots",
        back_populates="time_slots",
        viewonly=True,
        lazy="raise",
    )
    
    def __repr__(self):
        return f"<TimeSlot {self.id}>"

    def __str__(self):
        return f"<TimeSlot {self.id}>"
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class GroupTimeSlot(Base):
    __tablename__ = "group_time_slots"
    id = None
    
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True)
    time_slot_id: Mapped[int] = mapped_column(ForeignKey("time_slots.id", ondelete="RESTRICT"), primary_key=True)

    group: Mapped["Group"] = relationship("Group", back_populates="time_slot_links", lazy="raise")
    time_slot: Mapped["TimeSlot"] = relationship("TimeSlot", back_populates="group_links", lazy="raise")

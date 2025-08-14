from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String

from database.base import Base


class Group(Base):
    __tablename__ = "groups"

    name: Mapped[str] = mapped_column(String(16), nullable=False)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id", ondelete="RESTRICT"), nullable=False)
    
    program: Mapped["Program"] = relationship("Program", back_populates="groups", lazy="raise")
    
    time_slot_links: Mapped[List["GroupTimeSlot"]] = relationship(
        back_populates="group",
        lazy="raise",
        cascade="all, delete-orphan",
    )

    time_slots: Mapped[List["TimeSlot"]] = relationship(
        secondary="group_time_slots",
        back_populates="groups",
        viewonly=True,
        lazy="raise",
    )
    
    def __repr__(self):
        return f"<Group {self.name}>"

    def __str__(self):
        return f"<Group {self.name}>"
from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import CheckConstraint, String, Integer, Text, Boolean, Enum

from core.enums import ProgramLevel
from database.base import Base

from sqlalchemy.orm import Mapped, mapped_column

ProgramLevelDB = Enum(
    ProgramLevel,
    name="program_level",
    create_type=True,
    native_enum=True,
)


class Program(Base):
    __tablename__ = "programs"
    __table_args__ = (
    CheckConstraint("min_age >= 5 AND min_age <= 13", name="chk_min_age_bounds"),
    CheckConstraint("max_age >= 6 AND max_age <= 18", name="chk_max_age_bounds"),
    CheckConstraint("min_age <= max_age", name="chk_age_order"),
)

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    short_name: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True, default=None)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    min_age: Mapped[int] = mapped_column(Integer, nullable=False, index=True)   
    max_age: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    program_level: Mapped[ProgramLevel | None] = mapped_column(ProgramLevelDB, nullable=True, default=None)
    navigator_link: Mapped[str] = mapped_column(String(512), nullable=False)
    requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    
    groups: Mapped[List["Group"]] = relationship("Group", back_populates="program", lazy="raise", cascade="all, delete-orphan")
    
    __mapper_args__ = {"version_id_col": version}

    def __repr__(self):
        return f"<Program {self.name}>"

    def __str__(self):
        return f"<Program {self.name}>"

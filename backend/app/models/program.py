from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import CheckConstraint, String, Integer, Text, Boolean
from core.enums import ProgramCategory
from database.base import Base


class Program(Base):
    __tablename__ = "programs"
    __table_args__ = (CheckConstraint("min_age <= max_age", name="min_age_max_age_check"), CheckConstraint("min_age >= 0", name="min_age_check"), CheckConstraint("max_age <= 18", name="max_age_check"))

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    short_name: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True, default=None)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    min_age: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    max_age: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    program_level: Mapped[str | None] = mapped_column(String(50), nullable=True, default=None)
    category: Mapped[str] = mapped_column(String(50), nullable=False, server_default=ProgramCategory.COMPUTER_SCIENCE.value)
    navigator_link: Mapped[str] = mapped_column(String(512), nullable=False)
    requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    def __repr__(self):
        return f"<Program {self.name}>"

    def __str__(self):
        return f"<Program {self.name}>"

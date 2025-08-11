from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Text, Boolean

from app.database.base import Base


class Program(Base):
    __tablename__ = "programs"

    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    min_age: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    max_age: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    navigator_link: Mapped[str] = mapped_column(String(512), nullable=False)
    requirements: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    image_url: Mapped[str] = mapped_column(String(512), nullable=True)

    def __repr__(self):
        return f"<Program {self.name}>"

    def __str__(self):
        return f"<Program {self.name}>"

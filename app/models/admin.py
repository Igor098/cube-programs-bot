from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean

from app.database.base import Base


class Admin(Base):
    __tablename__ = "admins"

    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    telegram_id: Mapped[int] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<Admin {self.username}>"

    def __str__(self):
        return f"<Admin {self.username}>"

from datetime import date

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Date
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Todo(Base):
    __tablename__ = 'contacts'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150))
    surname: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(unique=True)
    phone: Mapped[str] = mapped_column()
    birthday: Mapped[date] = mapped_column(Date)
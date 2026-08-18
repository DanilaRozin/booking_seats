from sqlalchemy import CheckConstraint, ForeignKey, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from core.base_model import Base
from core.constants import TABLE_DESC_LENGTH


class Table(Base):
    """Модель столов в кафе."""

    cafe_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('cafes.id'),
        primary_key=True,
    )
    seat_number: Mapped[int] = mapped_column(
        SmallInteger,
        CheckConstraint('seat_number >= 1'),
    )
    description: Mapped[str | None] = mapped_column(
        String(TABLE_DESC_LENGTH),
        nullable=True,
    )

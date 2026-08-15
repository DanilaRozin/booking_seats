from sqlalchemy import CheckConstraint, ForeignKey, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from core.base_model import Base
from core.constants import TABLE_DESC_LENGTH


class Table(Base):
    """Модель столов в кафе."""

    cafe_id: Mapped[int] = mapped_column(Integer, ForeignKey('cafe.id'))
    seat_count = Mapped[int] = mapped_column(
        SmallInteger,
        CheckConstraint('seat_count >= 1'),
    )
    description: Mapped[str] = mapped_column(
        String(TABLE_DESC_LENGTH),
        nullable=True,
    )

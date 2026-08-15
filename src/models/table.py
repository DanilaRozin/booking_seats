from sqlalchemy import CheckConstraint, ForeignKey, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from core.base_model import Base


class Table(Base):
    """Модель столов в кафе."""

    cafe_id: Mapped[int] = mapped_column(Integer, ForeignKey('cafe.id'))
    seats_amount = Mapped[int] = mapped_column(
        SmallInteger,
        CheckConstraint('seats_amount >= 1'),
    )
    description: Mapped[str] = mapped_column(String, nullable=True)

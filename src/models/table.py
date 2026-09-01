from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.base_model import Base
from core.constants import TABLE_DESC_LENGTH

if TYPE_CHECKING:
    from models.booking import BookingTableSlot
    from models.cafe import Cafe


class Table(Base):
    """Модель столов в кафе."""

    __tablename__ = 'tables'

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
    cafe: Mapped['Cafe'] = relationship(
        back_populates='tables',
        lazy='selectin',
    )

    booking_table_slots: Mapped[list['BookingTableSlot']] = relationship(
        back_populates='table',
        lazy='selectin',
    )

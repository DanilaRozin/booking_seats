from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, ForeignKeyConstraint, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.base_model import Base
from core.constants import BookingStatus

if TYPE_CHECKING:
    from models.cafe import Cafe
    from models.slots import Slot
    from models.table import Table
    from models.user import User


class Booking(Base):
    """Модель бронирования."""

    __tablename__ = 'bookings'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    cafe_id: Mapped[int] = mapped_column(ForeignKey('cafes.id', ondelete='RESTRICT'), nullable=False)
    guest_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    note: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus, name='booking_status_enum'),
        default=BookingStatus.BOOKING,
        nullable=False,
    )
    booking_date: Mapped[date] = mapped_column(Date, nullable=False)
    user: Mapped['User'] = relationship(
        back_populates='bookings',
        lazy='selectin',
    )
    cafe: Mapped['Cafe'] = relationship(
        back_populates='bookings',
        lazy='selectin',
    )
    tables_slots: Mapped[list['BookingTableSlot']] = relationship(
        back_populates='booking',
        lazy='selectin',
        cascade='all, delete-orphan',
    )


class BookingTableSlot(Base):
    """Связь бронирования со столом и временным слотом."""

    __tablename__ = 'booking_table_slots'

    booking_id: Mapped[int] = mapped_column(ForeignKey('bookings.id', ondelete='CASCADE'), nullable=False)
    cafe_id: Mapped[int] = mapped_column(Integer, nullable=False)
    table_id: Mapped[int] = mapped_column(Integer, nullable=False)
    slot_id: Mapped[int] = mapped_column(ForeignKey('slots.id', ondelete='RESTRICT'), nullable=False)

    booking: Mapped['Booking'] = relationship(
        back_populates='tables_slots',
    )
    table: Mapped['Table'] = relationship(back_populates='booking_table_slots')
    slot: Mapped['Slot'] = relationship(back_populates='booking_table_slots')

    __table_args__ = (
        ForeignKeyConstraint(
            ['cafe_id', 'table_id'],
            ['tables.cafe_id', 'tables.id'],
            ondelete='RESTRICT',
        ),
    )

from __future__ import annotations

from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.base_model import Base
from core.constants import SLOT_DESC_LENGTH

if TYPE_CHECKING:
    from cafe import Cafe

    from models.booking import BookingTableSlot


class Slot(Base):
    """Модель временных слотов."""

    __tablename__ = 'slots'

    cafe_id: Mapped[int] = mapped_column(ForeignKey('cafes.id', ondelete='RESTRICT'), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    description: Mapped[str | None] = mapped_column(
        String(SLOT_DESC_LENGTH),
        nullable=True,
    )
    cafe: Mapped['Cafe'] = relationship(
        back_populates='slots',
        lazy='selectin',
    )
    booking_table_slots: Mapped[list['BookingTableSlot']] = relationship(
        back_populates='slot',
        lazy='selectin',
    )

    __table_args__ = (
        CheckConstraint(
            'end_time > start_time',
            name='ck_slots_end_gt_start',
        ),
    )

from __future__ import annotations

from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.base_model import Base

if TYPE_CHECKING:
    from cafe import Cafe


class Slot(Base):
    """Модель временных слотов."""

    __tablename__ = 'slots'

    cafe_id: Mapped[int] = mapped_column(ForeignKey('cafes.id', ondelete='RESTRICT'), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    description: Mapped[str | None] = mapped_column(
        String(),
        nullable=True,
    )
    cafe: Mapped['Cafe'] = relationship(
        back_populates='slots',
        lazy='selectin',
        foreign_keys=[cafe_id],
    )

    __table_args__ = (
        CheckConstraint(
            'end_time > start_time',
            name='ck_slots_end_gt_start',
        ),
    )

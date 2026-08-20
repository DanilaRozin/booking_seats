from datetime import time

from sqlalchemy import CheckConstraint, ForeignKey, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base_model import Base


class Slot(Base):
    """Модель временных слотов."""

    cafe_id: Mapped[int] = mapped_column(ForeignKey('cafes.id', ondelete='RESTRICT'), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    description: Mapped[str | None] = mapped_column(
        String(),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    cafe = relationship('Cafe', back_populates='slots', lazy='selectin')

    __table_args__ = (
        CheckConstraint(
            'end_time > start_time',
            name='ck_slots_end_gt_start',
        ),
    )

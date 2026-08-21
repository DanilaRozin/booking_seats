from __future__ import annotations

from sqlalchemy import SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.time_slots import Slot

from core.base_model import Base


class Cafe(Base):
    """Модель Кафе."""

    last_table_number: Mapped[int] = mapped_column(
        SmallInteger,
        default=0,
    )
    slots: Mapped[list[Slot]] = relationship(
        back_populates='cafe"',
        lazy='selectin',
        cascade='all, delete-orphan',
    )

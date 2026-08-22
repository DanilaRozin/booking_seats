from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.base_model import Base

if TYPE_CHECKING:
    from slots import Slot


class Cafe(Base):
    """Модель Кафе."""

    __tablename__ = 'cafes'

    last_table_number: Mapped[int] = mapped_column(
        SmallInteger,
        default=0,
    )
    slots: Mapped[list['Slot']] = relationship(
        back_populates='cafe',
        lazy='selectin',
        cascade='all, delete-orphan',
    )

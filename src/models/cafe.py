import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import SmallInteger, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.base_model import Base

if TYPE_CHECKING:
    from models.slots import Slot
    from models.table import Table
    from models.user import User


class Cafe(Base):
    """Модель кафе."""

    __tablename__ = 'cafes'

    name: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
    )
    address: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
    )
    phone: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        default=None,
    )
    photo_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid,
        nullable=True,
        default=None,
    )
    managers: Mapped[list['User']] = relationship(
        'User',
        back_populates='managed_cafe_id',
        lazy='selectin',
    )
    last_table_number: Mapped[int] = mapped_column(
        SmallInteger,
        default=0,
    )
    tables: Mapped[list['Table']] = relationship(back_populates='cafe')
    slots: Mapped[list['Slot']] = relationship(
        back_populates='cafe',
        lazy='selectin',
        cascade='all, delete-orphan',
    )

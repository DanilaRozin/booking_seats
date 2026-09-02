import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import SmallInteger, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.action import action_cafe_table
from models.dish import dish_cafe_table

from core.base_model import Base

if TYPE_CHECKING:
    from models.action import Action
    from models.booking import Booking
    from models.dish import Dish
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
    dishes: Mapped[list['Dish']] = relationship(
        back_populates='cafe',
        lazy='selectin',
        secondary=dish_cafe_table,
    )
    actions: Mapped[list['Action']] = relationship(
        back_populates='cafe',
        lazy='selectin',
        secondary=action_cafe_table,
    bookings: Mapped[list['Booking']] = relationship(
        back_populates='cafe',
        lazy='selectin',
    )

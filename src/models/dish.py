import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Float, ForeignKey, String, Table, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.base_model import Base

if TYPE_CHECKING:
    from models.cafe import Cafe

dish_cafe_table = Table(
    'dish_cafe_table',
    Base.metadata,
    Column('cafe_id', ForeignKey('cafes.id', ondelete='CASCADE'), primary_key=True),
    Column('dish_id', ForeignKey('dishes.id', ondelete='CASCADE'), primary_key=True),
)


class Dish(Base):
    """Модель блюд в сети кафе."""

    __tablename__ = 'dishes'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String)
    photo_id: Mapped[uuid.UUID] = mapped_column(Uuid, default=uuid.uuid4)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default='true',
    )
    cafe: Mapped[list['Cafe']] = relationship(
        secondary=dish_cafe_table,
        back_populates='dishes',
        lazy='selectin',
    )

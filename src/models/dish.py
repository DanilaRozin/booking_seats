import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from core.base_model import Base


class Dish(Base):
    """Модель блюд в сети кафе."""

    __tablename__ = 'dishes'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String)
    photo_id: Mapped[uuid.UUID] = mapped_column(Uuid, default=uuid.uuid4)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default='true'
    )
    # cafe_id: Mapped[int] = mapped_column(
    #     Integer,
    #     ForeignKey('cafes.id'),
    #     primary_key=True,
    # )

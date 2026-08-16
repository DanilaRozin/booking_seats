import uuid
from typing import List

from sqlalchemy import UUID, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.base_model import Base

cafe_manager_connect = Table(
    'cafes_managers',
    Base.metadata,
    Column('cafe_id', UUID(as_uuid=True), ForeignKey('cafes.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
)


class Cafe(Base):
    """Модель кафе."""

    name: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
    )
    address: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )
    phone: Mapped[str] = mapped_column(
        String(15),
        unique=True,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(String)
    photo_id: Mapped[uuid.UUID] = mapped_column(UUID, default=uuid.uuid4)
    managers: Mapped[List['User']] = relationship(  # noqa # type: ignore
        secondary=cafe_manager_connect,
        back_populates='managed_cafes',
    )

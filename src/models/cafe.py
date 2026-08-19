import uuid

from sqlalchemy import Column, ForeignKey, Integer, String, Table, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base, CommonMixin

cafe_manager_connect = Table(
    'cafes_managers',
    Base.metadata,
    Column('cafe_id', Integer, ForeignKey('cafe.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
)


class Cafe(CommonMixin, Base):
    """Модель кафе."""

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
    description: Mapped[str] = mapped_column(String)
    photo_id: Mapped[uuid.UUID] = mapped_column(Uuid, default=uuid.uuid4)
    managers: Mapped[list['User']] = relationship(  # noqa # type: ignore
        secondary=cafe_manager_connect,
        back_populates='managed_cafes',
    )

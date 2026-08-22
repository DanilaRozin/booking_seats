import uuid

from sqlalchemy import String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.table import Table
from models.user import User

from core.base_model import Base

__all__ = [
    'Base',
    'Cafe',
    'Table',
    'User',
]


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
    description: Mapped[str] = mapped_column(String)
    photo_id: Mapped[uuid.UUID] = mapped_column(Uuid, default=uuid.uuid4)
    managers: Mapped[list['User']] = relationship(  # noqa # type: ignore
        'User',
        back_populates='managed_cafe_id',
    )

    # last_table_number: Mapped[int] = mapped_column(
    #     SmallInteger,
    #     default=0,
    # )

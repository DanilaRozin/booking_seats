import uuid
from typing import TYPE_CHECKING

from sqlalchemy import SmallInteger, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.base_model import Base

if TYPE_CHECKING:
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
    description: Mapped[str] = mapped_column(String)
    photo_id: Mapped[uuid.UUID] = mapped_column(Uuid, default=uuid.uuid4)
    managers: Mapped[list['User']] = relationship(
        'User',
        back_populates='managed_cafe_id',
    )
    tables: Mapped[list['Table']] = relationship(back_populates='cafe')
    last_table_number: Mapped[int] = mapped_column(
        SmallInteger,
        default=0,
    )

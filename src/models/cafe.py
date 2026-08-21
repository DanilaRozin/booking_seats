import uuid

from sqlalchemy import String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.base_model import Base


class Cafe(Base):
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
        'User',
        back_populates='managed_cafe_id',
    )

    # last_table_number: Mapped[int] = mapped_column(
    #     SmallInteger,
    #     default=0,
    # )

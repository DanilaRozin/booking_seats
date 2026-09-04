import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, ForeignKey, String, Table, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.base_model import Base

if TYPE_CHECKING:
    from models.cafe import Cafe

action_cafe_table = Table(
    'action_cafe_table',
    Base.metadata,
    Column('cafe_id', ForeignKey('cafes.id', ondelete='CASCADE'), primary_key=True),
    Column('action_id', ForeignKey('actions.id', ondelete='CASCADE'), primary_key=True),
)


class Action(Base):
    """Базовая схема для модели 'Акций'."""

    __tablename__ = 'actions'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String)
    photo_id: Mapped[uuid.UUID] = mapped_column(Uuid, default=uuid.uuid4)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default='true',
    )
    cafe: Mapped[list['Cafe']] = relationship(
        secondary=action_cafe_table,
        back_populates='actions',
        lazy='selectin',
    )

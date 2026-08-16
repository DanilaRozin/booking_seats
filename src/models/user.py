from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import CheckConstraint, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.constants import NAME_MAX_LENGTH, RoleEnum
from src.core.db import Base, CommonMixin
from src.models.cafe import cafe_manager_connect


class User(SQLAlchemyBaseUserTable[int], Base, CommonMixin):
    """Модель пользователя."""

    username: Mapped[str] = mapped_column(String(NAME_MAX_LENGTH), nullable=False)
    phone: Mapped[str] = mapped_column(String(), nullable=True)
    tg_id: Mapped[str] = mapped_column(String(), nullable=True)
    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum, name='role_enum'),
        default=RoleEnum.USER,
        nullable=False,
    )
    managed_cafes: Mapped[list['Cafe']] = relationship(  # noqa # type: ignore
        secondary=cafe_manager_connect,
        back_populates='managers',
    )
    __table_args__ = (CheckConstraint('length(username) >= 5', name='name_min_length'),)

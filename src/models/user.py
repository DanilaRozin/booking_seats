from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import CheckConstraint, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from core.base_model import Base
from core.constants import NAME_MAX_LENGTH, RoleEnum


class User(SQLAlchemyBaseUserTable[int], Base):
    """Модель пользователя."""

    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(String(NAME_MAX_LENGTH), nullable=False)
    phone: Mapped[str] = mapped_column(String(), nullable=False, index=True)
    tg_id: Mapped[str] = mapped_column(String(), nullable=True)
    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum, name='role_enum'),
        default=RoleEnum.USER,
        nullable=False,
    )
    __table_args__ = (CheckConstraint('length(username) >= 5', name='name_min_length'),)

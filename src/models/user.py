from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.cafe import cafe_manager_connect

from core.base_model import Base


class User(Base):
    """Тестовая модель пользователя."""

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    managed_cafes: Mapped[list['Cafe']] = relationship(  # noqa # type: ignore
        secondary=cafe_manager_connect,
        back_populates='managers',
    )

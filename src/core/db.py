from datetime import datetime
from typing import AsyncIterator

from fastapi import HTTPException
from sqlalchemy import Integer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from src.core.settings import settings
from src.core.utils import utcnow_naive


class Base(DeclarativeBase):
    """Базовый класс для всех моделей проекта."""


class CommonMixin:
    """Общие поля и поведение, разделяемые между моделями (id, __tablename__)."""

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(Integer, primary_key=True, sort_order=-1)
    created_at: Mapped[datetime] = mapped_column(default=utcnow_naive, sort_order=2)
    updated_at: Mapped[datetime | None] = mapped_column(nullable=True, sort_order=3)


async_engine = create_async_engine(
    url=settings.db_url,
    pool_pre_ping=True,
)

session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Получение асинхронной сессии для FastAPI Depends."""
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            import traceback
            traceback.print_exc()
        # except SQLAlchemyError:
            await session.rollback()
            raise HTTPException(
                status_code=500,
                detail=f'Ошибка {str(e)} | тип {type(e).__name__}',
            )
            # raise HTTPException(status_code=500, detail='Ошибка при работе с БД')
        finally:
            await session.close()

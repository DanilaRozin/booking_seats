from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.settings import settings

async_engine = create_async_engine(
    url=settings.db_url,
    pool_pre_ping=True,
)

session_maker = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Контекстный менеджер для получения сессии БД (для FastAPI Depends)."""
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError:
            await session.rollback()
            raise HTTPException(status_code=500,
                                detail="Ошибка при работе с БД")

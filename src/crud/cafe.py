from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models.cafe import Cafe
from src.models.user import User
from src.schemas.cafe import CafeBase


class CRUDCafe(CRUDBase):
    """Класс работы с кафе."""

    async def get_cafe_id_by_name(
        self,
        cafe_name: str,
        session: AsyncSession,
    ) -> Optional[int]:
        """Метод возвращает id кафе по названию."""
        db_cafe_id = await session.execute(
            select(Cafe.id).where(
                Cafe.name == cafe_name,
            ),
        )
        return db_cafe_id.scalars().first()

    async def create(
        self,
        obj_in: CafeBase,
        session: AsyncSession,
        user: User = None,
    ) -> Cafe:
        """Метод создает кафе без привязки менеджеров."""
        db_obj = self.model(**obj_in.model_dump())
        db_obj.managers = []
        session.add(db_obj)
        await session.commit()
        await session.flush()
        return db_obj


cafe_crud = CRUDCafe(Cafe)

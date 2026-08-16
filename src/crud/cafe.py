from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from models.cafe import Cafe
from models.user import User
from schemas.cafe import CafeCreate


class CRUDCafe(CRUDBase):
    """Класс работы с кафе."""

    async def get_cafe_id_by_name(
        self,
        cafe_name: str,
        session: AsyncSession,
    ) -> Optional[int]:
        """Метод возвращает id объекта по названию."""
        db_cafe_id = await session.execute(
            select(Cafe.id).where(
                Cafe.name == cafe_name,
            ),
        )
        return db_cafe_id.scalars().first()

    async def create(
        self,
        obj_in: CafeCreate,
        session: AsyncSession,
    ) -> Cafe:
        """Метод записи в базу кафе с привязкой менеджеров."""
        obj_in_data = obj_in.model_dump()
        managers_id = obj_in_data.pop('managers_id', [])
        db_obj = self.model(**obj_in_data)
        if managers_id:
            query = select(User).where(User.id.in_(managers_id))
            result = await session.execute(query)
            found_managers = result.scalars().all()
            db_obj.managers = list(found_managers)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj


cafe_crud = CRUDCafe(Cafe)

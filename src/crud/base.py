from collections.abc import Sequence
from typing import Any, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import Base
from src.models.user import User


class CRUDBase:
    """Базовый круд."""

    def __init__(self, model: type[Base]) -> None:
        """Сохраняет модель, с которой будет работать этот CRUD."""
        self.model = model

    async def get(
        self,
        obj_id: int,
        session: AsyncSession,
    ) -> Any | None:
        """Возвращает объект по id или None, если не найден."""
        db_obj = await session.execute(select(self.model).where(self.model.id == obj_id))
        return db_obj.scalars().first()

    async def get_multi(self, session: AsyncSession) -> Sequence[Any]:
        """Возвращает все объекты модели."""
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    async def create(
        self,
        obj_in: object,
        session: AsyncSession,
        user: Optional[User] = None,
    ) -> object:
        """Универсальный метод записи в БД."""
        obj_in_data = obj_in.model_dump()
        if user is not None:
            obj_in_data['user_id'] = user.id
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db_obj: Any,
        obj_in: Any,
        session: AsyncSession,
    ) -> Any:
        """Универсальный метод обновления объекта в БД."""
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.flush()
        await session.refresh(db_obj)
        return db_obj

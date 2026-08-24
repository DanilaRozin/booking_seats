from collections.abc import Sequence
from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from core.base_model import Base

ModelT = TypeVar('ModelT', bound=Base)


class CRUDBase(Generic[ModelT]):
    """Класс для CRUD-операций."""

    def __init__(self, model: type[ModelT]) -> None:
        """Инициализирует объект для выполнения CRUD-операций.

        Args:
            model: Класс ORM-модели, над которой выполняются CRUD-операции.

        """
        self.model = model

    async def get(
        self,
        obj_id: int,
        session: AsyncSession,
        *conditions: ColumnElement[bool],
    ) -> ModelT | None:
        """Получает объект модели по идентификатору.

        Args:
            obj_id: Идентификатор объекта.
            session: Асинхронная сессия SQLAlchemy.
            *conditions: SQLAlchemy-условия для фильтрации объектов.
                Несколько условий объединяются оператором AND.

        Returns:
            Найденный объект модели или None, если объект не существует.

        """
        db_obj = await session.execute(
            select(self.model).where(self.model.id == obj_id, *conditions),
        )
        return db_obj.scalars().first()

    async def get_multi(
        self,
        session: AsyncSession,
        *conditions: ColumnElement[bool],
    ) -> Sequence[ModelT]:
        """Получает все объекты модели.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            *conditions: SQLAlchemy-условия для фильтрации объектов.
                Несколько условий объединяются оператором AND.

        Returns:
            Список объектов модели.

        """
        db_objs = await session.execute(select(self.model).where(*conditions))
        return db_objs.scalars().all()

    async def create(
        self,
        obj_in: BaseModel,
        session: AsyncSession,
        **additional_attrs: object,
    ) -> ModelT:
        """Создаёт объект модели.

        Args:
            obj_in: Схема с данными для создания объекта.
            session: Асинхронная сессия SQLAlchemy.
            **additional_attrs: Дополнительные атрибуты модели, непереданные в схеме.

        Returns:
            Созданный объект модели.

        """
        obj_in_data = obj_in.model_dump()
        obj_in_data.update(additional_attrs)

        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        return db_obj

    async def update(
        self,
        db_obj: ModelT,
        obj_in: BaseModel,
        session: AsyncSession,
    ) -> ModelT:
        """Обновляет объект модели.

        Args:
            db_obj: ORM-объект, который требуется обновить.
            obj_in: Схема с данными для обновления объекта.
            session: Асинхронная сессия SQLAlchemy.

        Returns:
            Обновлённый объект модели.

        """
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field in update_data:
                setattr(db_obj, field, value)
        session.add(db_obj)
        await session.commit()
        return db_obj

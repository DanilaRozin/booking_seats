from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDBase:
    """Инициализатор класса."""

    def __init__(self, model) -> None:  # noqa: ANN001
        """Принимает на вход модель, с которой нужно выполнить операции."""
        self.model = model

    async def get(
        self,
        obj_id: int,
        session: AsyncSession,
    ) -> object:
        """Универсальный метод получения объекта из БД по id."""
        db_obj = await session.execute(
            select(self.model).where(
                self.model.id == obj_id,
            ),
        )
        return db_obj.scalars().first()

    async def get_multi(
        self,
        session: AsyncSession,
    ) -> list:
        """Универсальный метод для получения всех объектов заданной модели."""
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    async def create(
        self,
        obj_in: object,
        session: AsyncSession,
        # user: Optional[User] = None,
    ) -> object:
        """Универсальный метод записи в БД."""
        obj_in_data = obj_in.model_dump()
        # if user is not None:
        #     obj_in_data['user_id'] = user.id
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db_obj: object,
        obj_in: object,
        session: AsyncSession,
    ) -> object:
        """Универсальный метод редактирования записи в БД."""
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.model_dump(exclude_unset=True)
        update_data.pop('managers_id', None)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def remove(
        self,
        db_obj: object,
        session: AsyncSession,
    ) -> None:
        """Универсальный метод удаления записи из БД."""
        await session.delete(db_obj)
        await session.commit()
        return db_obj

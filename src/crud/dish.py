from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from models import Cafe, Dish
from schemas.dish import DishCreate, DishUpdate


class CRUDDish(CRUDBase[Dish, DishCreate, DishUpdate]):
    """Класс для CRUD-операций с ORM-моделью блюд."""

    async def create(
        self,
        obj_in: DishCreate,
        session: AsyncSession,
    ) -> Dish:
        """Метод создает блюдо и привязыввет его к кафе из cafes_id."""
        obj_in_data = obj_in.model_dump()
        cafes_id = obj_in_data.pop('cafes_id')
        cafes = (await session.execute(select(Cafe).where(Cafe.id.in_(cafes_id)))).scalars().all()
        db_obj = self.model(**obj_in_data, cafes=cafes)
        session.add(db_obj)
        await session.commit()
        return db_obj

    async def update(
        self,
        db_obj: Dish,
        obj_in: DishUpdate,
        session: AsyncSession,
    ) -> Dish:
        """Метод обновляет информацию о блюде."""
        update_data = obj_in.model_dump(exclude_unset=True)
        cafes_id = update_data.pop('cafes_id', None)
        if cafes_id is not None:
            db_obj.cafes = (await session.execute(select(Cafe).where(Cafe.id.in_(cafes_id)))).scalars().all()

        for field, value in update_data.items():
            setattr(db_obj, field, value)
        session.add(db_obj)
        await session.commit()
        return db_obj


dish_crud = CRUDDish(Dish)

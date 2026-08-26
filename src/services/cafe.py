from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.cafe import Cafe
from models.user import User


async def update_cafe_managers_service(
    cafe_id: int,
    session: AsyncSession,
    managers_id: list[int] | None = None,
) -> list[User]:
    """Сервисный метод обновляет связь менеджеры-кафе."""
    query = select(User).where(User.id.in_(managers_id))
    result_managers = await session.execute(query)
    found_managers = list(result_managers.scalars().all())
    for manager in found_managers:
        manager.cafe_id = cafe_id
    await session.flush()
    return found_managers


async def add_managers_to_cafe_by_id(
    cafe_obj: Cafe,
    session: AsyncSession,
) -> Cafe:
    """Сервисный метод получения списка менеджеров."""
    cafe_managers_link = select(Cafe).where(Cafe.id == cafe_obj.id).options(selectinload(Cafe.managers))
    result = await session.execute(cafe_managers_link)
    refreshed = result.scalar_one_or_none()
    cafe_obj.managers = refreshed.managers if refreshed else []
    return cafe_obj

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
    if not managers_id:
        print(f'Список менеджеров не передан: {managers_id}')
        return []

    query = select(User).where(User.id.in_(managers_id))
    print(f'Получили модель пользователя: {query}')
    result_managers = await session.execute(query)
    print(f'Запросили асинхронно: {result_managers}')
    found_managers = list(result_managers.scalars().all())
    print(f'Получили список менеджеров {found_managers}')
    for manager in found_managers:
        manager.cafe_id = cafe_id
        print(f'Перебираем этот список и заполняем ID-менеджера кафе {manager.cafe_id} значением {cafe_id}')
    await session.flush()
    print(f'Итоговой список выглядит так: {found_managers}')
    return found_managers


async def add_managers_to_cafe_by_id(
    cafe_obj: Cafe,
    session: AsyncSession,
) -> Cafe:
    """Сервисный метод получения списка менеджеров."""
    cafe_managers_link = select(Cafe).where(Cafe.id == cafe_obj.id).options(selectinload(Cafe.managers))
    print(f'связь найдена: {cafe_managers_link}')
    result = await session.execute(cafe_managers_link)
    refreshed = result.scalar_one_or_none()
    cafe_obj.managers = refreshed.managers if refreshed else []
    print(f'Список менеджеров подгружен: {cafe_obj.managers}')
    print(f'Сам объект кафе: {cafe_obj}')
    return cafe_obj

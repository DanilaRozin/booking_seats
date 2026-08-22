from fastapi import HTTPException, status
from sqlalchemy import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession

from crud.slots import slot_crud
from models import Slot
from schemas.user import UserInfo

from core.constants import RoleEnum


async def get_slot_for_user(
    slot_id: int,
    cafe_id: int,
    user: UserInfo,
    session: AsyncSession,
) -> Slot:
    """Получает слот для конкретного пользователя."""
    conditions = [Slot.cafe_id == cafe_id]

    if user.role not in (RoleEnum.ADMIN, RoleEnum.MANAGER):
        conditions.append(Slot.is_active)

    slot = await slot_crud.get(
        slot_id,
        session,
        *conditions,
    )

    if slot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Слот {slot_id} не найден. Он не существует в кафе {cafe_id}.',
        )
    return slot


def get_slot_filters_for_user(user: UserInfo) -> list[ColumnElement]:
    """Возвращает список условий SQLAlchemy для фильтрации слотов по правам пользователя."""
    if user.role in (RoleEnum.ADMIN, RoleEnum.MANAGER):
        return []
    return [Slot.is_active]

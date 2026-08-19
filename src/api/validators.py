from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.time_slots import slot_crud
from src.models.cafe import Cafe
from src.models.time_slots import Slot


async def check_cafes_exists(
    cafe_id: int,
    session: AsyncSession,
) -> Cafe:
    """Проверка кафе на существование."""
    cafe = await slot_crud.get(
        cafe_id,
        session,
    )
    if cafe is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Кафе {cafe_id} не найдено.',
        )
    return cafe


async def check_slots_exists(
    slot_id: int,
    session: AsyncSession,
) -> Slot:
    """Проверка слота на существование."""
    slot = await slot_crud.get(
        slot_id,
        session,
    )
    if slot is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Временной слот {slot_id} не найден.',
        )
    return slot

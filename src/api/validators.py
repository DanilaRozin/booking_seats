from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from crud import table_crud
from crud.time_slots import slot_crud
from models import Table
from models.cafe import Cafe


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
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Кафе {cafe_id} не найдено.',
        )
    return cafe


async def check_table_exists(
    cafe_id: int,
    table_id: int,
    session: AsyncSession,
) -> Table:
    """Проверка существования в БД стола в кафе."""
    table = await table_crud.get(table_id, session, Table.cafe_id == cafe_id)
    if table is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Стола не существует!',
        )
    return table

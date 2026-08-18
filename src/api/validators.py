from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from crud import cafe_crud, table_crud
from models import Table


async def check_cafe_exists(
    cafe_id: int,
    session: AsyncSession,
) -> Table:
    """Проверка существования кафе в БД."""
    cafe = await cafe_crud.get(cafe_id, session)
    if cafe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Кафе не существует!',
        )
    return cafe


async def check_table_exists(
    cafe_id: int,
    table_id: int,
    session: AsyncSession,
) -> Table:
    """Проверка существования в БД стола в кафе."""
    await check_cafe_exists(cafe_id, session)
    table = await table_crud.get(table_id, session, Table.cafe_id == cafe_id)
    if table is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Стола не существует!',
        )
    return table

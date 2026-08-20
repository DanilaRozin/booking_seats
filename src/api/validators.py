from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from crud.cafe import cafe_crud
from crud.table import table_crud
from models.cafe import Cafe
from models.table import Table


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


async def check_name_duplicate(
    cafe_name: str,
    session: AsyncSession,
) -> None:
    """Проверка уникальности названия кафе."""
    cafe_id = await cafe_crud.get_cafe_id_by_name(
        cafe_name,
        session,
    )
    if cafe_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Кафе с таким названием уже существует',
        )


async def check_cafe_exists(
    cafe_id: int,
    session: AsyncSession,
) -> Cafe:
    """Проверка наличия кафе в базе."""
    db_cafe = await cafe_crud.get(
        cafe_id,
        session,
    )
    if db_cafe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Кафе не найдено в базе',
        )
    return db_cafe

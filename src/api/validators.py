from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.cafe import cafe_crud
from src.models.cafe import Cafe


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

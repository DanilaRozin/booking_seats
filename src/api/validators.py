from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from crud import cafe_crud, table_crud
from models import Table
from schemas.user import UserCreate

from core.user import UserManager


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
) -> object:
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


async def existing_user(user_create: UserCreate, user_manager: UserManager) -> None:
    """Проверка заняты ли username, email или phone(номер телефона)."""
    if await user_manager.user_db.get_by_email(user_create.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Указанный email занят.',
        )

    if await user_manager.user_db.get_by_phone(user_create.phone) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Указанный номер телефона занят.',
        )
    if await user_manager.user_db.get_by_username(user_create.username) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Указанный username занят.',
        )

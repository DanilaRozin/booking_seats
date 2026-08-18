from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from crud import table_crud
from models import Table
from schemas.user import UserCreate

from core.user import UserManager


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

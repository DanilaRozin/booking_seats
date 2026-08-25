from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from crud import cafe_crud
from crud.base import CRUDBase
from schemas.user import UserCreate

from core.base_model import Base
from core.user import UserManager


async def check_object_exists[
    ModelT: Base,
    CreateSchemaT: BaseModel,
    UpdateSchemaT: BaseModel,
](
    crud: CRUDBase[ModelT, CreateSchemaT, UpdateSchemaT],
    obj_id: int,
    session: AsyncSession,
    *conditions: ColumnElement[bool],
) -> ModelT:
    """Проверка существования объекта в БД."""
    obj = await crud.get(obj_id, session, *conditions)
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Объект модели {crud.model.__name__} не найден.',
        )
    return obj


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

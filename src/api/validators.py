from uuid import UUID

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from crud import cafe_crud, dish_crud
from crud.base import CRUDBase
from models import User
from schemas.user import UserCreate
from services.media import MediaService

from core.base_model import Base
from core.constants import RoleEnum
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


async def check_dish_exists(
    dish_id: int,
    session: AsyncSession,
) -> object:
    """Проверка существования в БД блюда."""
    db_dish = await dish_crud.get(
        dish_id,
        session,
    )
    if db_dish is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Блюдо не найдено в базе',
        )
    return db_dish


def existing_image(photo_id: UUID) -> None:
    """Проверка существует ли файл картинки."""
    try:
        MediaService.get_image_path(photo_id)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Не найден файл изображения кафе.',
        )


async def validate_managers_id(
    managers_id: list[int],
    session: AsyncSession,
) -> list[int]:
    """Проверка на валидность списка менеджеров."""
    stmt = select(User).where(
        User.id.in_(managers_id),
        User.role == RoleEnum.MANAGER,
    )
    result = await session.execute(stmt)
    db_managers = result.scalars().all()
    if len(db_managers) != len(managers_id):
        bad_managers = set(managers_id) - set(user.id for user in db_managers)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f'Нельзя назначить несуществующих менеджеров {list(bad_managers)}',
        )
    is_not_free = [user.id for user in db_managers if user.cafe_id is not None]
    if is_not_free:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f'Нельзя назначить несвободных менеджеров: {is_not_free}',
        )

    return list(db_managers)

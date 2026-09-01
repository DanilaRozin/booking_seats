from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.validators import (
    check_name_duplicate,
    check_object_exists,
    existing_image,
    validate_managers_id,
)
from crud.cafe import cafe_crud
from models import Cafe, User
from schemas.cafe import (
    CafeBase,
    CafeCreate,
    CafeInfo,
    CafeUpdate,
)

from core.constants import RoleEnum
from core.db import get_session
from core.user import current_admin, current_manager, current_user

router = APIRouter()
SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get(
    '/',
    summary='Получение списка кафе',
    response_model=list[CafeInfo],
)
async def get_all_cafe(
    session: SessionDep,
    user: Optional[User] = Depends(current_user),
    show_active: Annotated[
        bool | None,
        Query(description='Фильтрация работает только для менеджеров и админа'),
    ] = None,
) -> list[Cafe]:
    """Получение списка кафе.

    Для администраторов и менеджеров - все кафе (с возможностью выбора),
    для пользователей - только активные.

    """
    conditions = []

    if user.role == RoleEnum.USER:
        conditions.append(Cafe.is_active.is_(True))
        show_active = True

    if user.role in [RoleEnum.MANAGER, RoleEnum.ADMIN] and show_active is None:
        pass

    else:
        conditions.append(Cafe.is_active.is_(show_active))

    return await cafe_crud.get_multi(session, *conditions)


@router.post(
    '/',
    summary='Создание нового кафе',
    response_model=CafeInfo,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(current_admin)],
)
async def create_new_cafe(
    cafe_in: CafeCreate,
    session: SessionDep,
) -> Cafe:
    """Создает новое кафе.

    Только для администраторов.
    """
    await check_name_duplicate(cafe_in.name, session)
    cafe_base_data = CafeBase(**cafe_in.model_dump())

    new_cafe = await cafe_crud.create(obj_in=cafe_base_data, session=session)

    attached_managers = await validate_managers_id(
        cafe_in.managers_id,
        session,
    )

    if cafe_in.photo_id:
        existing_image(cafe_in.photo_id)

    new_cafe.managers = attached_managers
    await session.commit()
    await session.refresh(new_cafe)
    return new_cafe


@router.get(
    '/{cafe_id}',
    summary='Получение информации о кафе по его ID',
    response_model=CafeInfo,
)
async def get_cafe_by_id(
    cafe_id: int,
    session: SessionDep,
    user: Optional[User] = Depends(current_user),
) -> Cafe:
    """Получение информации о кафе по его ID.

    Для администраторов и менеджеров - все кафе,
    для пользователей - только активные.
    """
    db_cafe = await cafe_crud.get(cafe_id, session)

    if not db_cafe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Кафе отсутствует в БД',
        )

    is_staff = user and user.role in ['ADMIN', 'MANAGER']
    if not is_staff and not db_cafe.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Доступно только для менеджера или админа',
        )
    await session.commit()
    await session.refresh(db_cafe)
    return db_cafe


@router.patch(
    '/{cafe_id}',
    summary='Обновление информации о кафе по его ID',
    response_model=CafeInfo,
    response_model_exclude_none=True,
    dependencies=[Depends(current_manager)],
)
async def partial_update_cafe(
    cafe_id: int,
    obj_in: CafeUpdate,
    session: SessionDep,
    user: Optional[User] = Depends(current_user),
) -> Cafe:
    """Обновление информации о кафе по его ID.

    Только для администраторов и менеджеров.
    """
    if user.role == RoleEnum.MANAGER:
        db_cafe = await check_object_exists(
            cafe_crud,
            cafe_id,
            session,
            Cafe.id == user.cafe_id,
        )
    db_cafe = await check_object_exists(cafe_crud, cafe_id, session)

    if obj_in.name is not None:
        await check_name_duplicate(obj_in.name, session)

    if obj_in.photo_id:
        existing_image(obj_in.photo_id)

    db_cafe = await cafe_crud.update(db_cafe, obj_in, session)

    if obj_in.managers_id:
        attached_managers = await validate_managers_id(
            obj_in.managers_id,
            session,
        )
        db_cafe.managers = attached_managers

    await session.commit()
    await session.refresh(db_cafe)
    return db_cafe

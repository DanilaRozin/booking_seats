import traceback
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.services.cafe import (
    add_managers_to_cafe_by_id,
    update_cafe_managers_service,
)
from api.validators import check_name_duplicate, check_object_exists
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
from core.user import current_manager, current_superuser, current_user

router = APIRouter()
SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post(
    '/',
    response_model=CafeInfo,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(current_superuser)],
)
async def create_new_cafe(
    cafe_in: CafeCreate,
    session: SessionDep,
) -> Cafe:
    """Создать кафе. Доступ только у суперадминистратора."""
    try:
        await check_name_duplicate(cafe_in.name, session)
        cafe_base_data = CafeBase(**cafe_in.model_dump())

        new_cafe = await cafe_crud.create(obj_in=cafe_base_data, session=session)

        if cafe_in.managers_id:
            attached_managers = await update_cafe_managers_service(
                cafe_id=new_cafe.id,
                session=session,
                managers_id=cafe_in.managers_id,
            )

        new_cafe.managers = attached_managers

        return new_cafe

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f'Сбой {str(e)} | тип {type(e).__name__}')


@router.get(
    '/',
    response_model=list[CafeInfo],
)
async def get_all_cafe(
    session: SessionDep,
    user: Optional[User] = Depends(current_user),
    show_active: bool | None = None,
) -> list[Cafe]:
    """Получить список кафе. Только для зарегистрированных пользователей."""
    if user.role == RoleEnum.USER or (user.role == RoleEnum.MANAGER and show_active is None):
        show_active = True
    return await cafe_crud.get_multi(session)


@router.get(
    '/{cafe_id}',
    response_model=CafeInfo,
)
async def get_cafe_by_id(
    cafe_id: int,
    session: SessionDep,
    user: Optional[User] = Depends(current_user),
) -> Cafe:
    """Получить информацию о кафе по ID."""
    db_cafe = await cafe_crud.get(cafe_id, session)
    if not db_cafe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Кафе отсутствует в БД',
        )
    is_staff = user and user.role in ['ADMIN', 'MANAGER']
    if not is_staff:  # and not db_cafe.is_active
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Доступно только для менеджера или админа',
        )

    return await add_managers_to_cafe_by_id(db_cafe, session)


@router.patch(
    '/{cafe_id}',
    response_model=CafeInfo,
    response_model_exclude_none=True,
    dependencies=[Depends(current_manager)],
)
async def partial_update_cafe(
    cafe_id: int,
    obj_in: CafeUpdate,
    session: SessionDep,
) -> Cafe:
    """Редактировать кафе."""
    db_cafe = await check_object_exists(cafe_crud, cafe_id, session)

    if obj_in.name is not None:
        await check_name_duplicate(obj_in.name, session)

    db_cafe = await cafe_crud.update(
        db_cafe,
        obj_in,
        session,
    )

    db_cafe = await add_managers_to_cafe_by_id(db_cafe, session)

    if obj_in.managers_id is not None:
        attached_managers = await update_cafe_managers_service(
            cafe_id=db_cafe.id,
            session=session,
            managers_id=obj_in.managers_id,
        )
        db_cafe.managers = attached_managers

    await session.commit()
    return db_cafe

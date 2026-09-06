from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi_users import exceptions

from api import SessionDep, UserDep
from api.validators import check_object_exists, ensure_can_change_role, ensure_can_deactivate, existing_user
from crud.user import user_crud
from models import User
from schemas.user import UserCreate, UserInfo, UserUpdate
from tasks.booking_notifications.email_notifications import notify_registration

from core.user import UserManager, current_manager_without_cafe, get_user_manager

router = APIRouter()


@router.get(
    '',
    response_model=list[UserInfo],
    dependencies=[Depends(current_manager_without_cafe)],
    summary='Посмотреть список всех пользователей',
)
async def get_list_user_info(
    session: SessionDep,
    show_active: Annotated[
        bool | None,
        Query(description='Фильтр для просмотра активных или неактивных пользвоателей'),
    ] = None,
) -> Sequence[User]:
    """Возращает список состоящий из всех пользователей."""
    conditions = []
    if show_active is None:
        pass
    else:
        conditions.append(User.is_active.is_(show_active))

    return await user_crud.get_multi(session, *conditions)


# Регистрация пользователя
@router.post(
    '',
    response_model=UserInfo,
    status_code=status.HTTP_201_CREATED,
    summary='Регистрация пользователя',
)
async def register(
    user_create: UserCreate,
    request: Request,
    user_manager: UserManager = Depends(get_user_manager),
) -> User:
    """Регистрация пользователя.

    - **username**: юзернейм пользователя
    - **email**: адрес электронной почты
    - **phone**: номер телефона
    - **tg_id**: Telegram ID (опционально)
    - **password**: пароль
    """
    await existing_user(user_create, user_manager)
    try:
        user = await user_manager.create(user_create, safe=True, request=request)
    except exceptions.InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.reason,
        )

    notify_registration.delay(
        user_id=user.id,
        username=user.username,
        user_email=user.email,
    )
    return user


@router.get(
    '/me',
    response_model=UserInfo,
    response_model_exclude_none=True,
    summary='Посмотреть информацию о себе',
)
async def get_me_info(
    session: SessionDep,
    user: UserDep,
) -> User:
    """Возращает информацию о пользователе."""
    return await user_crud.get(obj_id=user.id, session=session)


@router.patch(
    '/me',
    response_model=UserInfo,
    response_model_exclude_none=True,
)
async def update_me_info(
    obj_in: UserUpdate,
    user: UserDep,
    user_manager: UserManager = Depends(get_user_manager),
    request: Request = None,
) -> User:
    """Обновляет данные текущего пользователя."""
    ensure_can_change_role(obj_in, user, user_obj=user, user_id=user.id)
    return await user_manager.update(obj_in, user, safe=True, request=request)


@router.get(
    '/{user_id}',
    response_model=UserInfo,
    dependencies=[Depends(current_manager_without_cafe)],
)
async def get_user_info_by_id(
    session: SessionDep,
    user_id: int,
) -> User:
    """Возвращает данные пользователя по id (для менеджеров и админов)."""
    return await check_object_exists(user_crud, user_id, session, check_active=False)


@router.patch(
    '/{user_id}',
    response_model=UserInfo,
)
async def update_user_info(
    session: SessionDep,
    obj_in: UserUpdate,
    user_id: int,
    request: Request,
    user: User = Depends(current_manager_without_cafe),
    user_manager: UserManager = Depends(get_user_manager),
) -> User:
    """Обновляет данные пользователя по id (для менеджеров и админов)."""
    user_obj = await check_object_exists(user_crud, user_id, session, check_active=False)
    ensure_can_deactivate(obj_in, user, user_obj=user_obj, user_id=user_id)
    ensure_can_change_role(obj_in, user, user_obj=user_obj, user_id=user_id)
    return await user_manager.update(obj_in, user_obj, request=request)

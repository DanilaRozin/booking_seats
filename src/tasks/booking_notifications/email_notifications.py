"""Задачи с E-mail уведомлений."""

from pathlib import Path
from typing import TYPE_CHECKING

from celery import Task
from loguru import logger

from services.send_email import _send_email
from tasks.booking_notifications.base_task import BaseTask

from core.celery_app import celery_app
from core.logging_config import contextualize_user
from core.settings import settings

if TYPE_CHECKING:
    from datetime import datetime

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / 'tasks' / 'templates'


@celery_app.task(
    name='notify_registration',
    base=BaseTask,
    bind=True,
)
def notify_registration(
    self: Task,
    user_id: int,
    username: str,
    user_email: str,
    service_name: str = settings.title,
) -> None:
    """Уведомляет о регистрации через Celery задачу.

    Args:
        self (Task): Экземпляр задачи.
        user_id (int): ID пользователя.
        username (str): Username пользователя.
        user_email (str): E-mail пользователя.
        service_name (str): Название сервиса.

    """
    with contextualize_user(username=username, user_id=user_id):
        logger.info('Отправка notify_registration | to={email}', email=user_email)
        html = (TEMPLATES_DIR / 'registration.html').read_text(encoding='utf-8')
        subject_msg = f'{service_name}: Регистрация пользователя {username}.'
        body_text_msg = f'Пользователь {username} зарегистрирован!'
        body_html_msg = html.format(
            text=body_text_msg,
            service_name=service_name,
        )
        _send_email(
            to_addr=user_email,
            subject=subject_msg,
            body_text=body_text_msg,
            body_html=body_html_msg,
        )


@celery_app.task(
    name='notify_client_booking',
    base=BaseTask,
    bind=True,
)
def notify_client_booking(
    self: Task,
    user_id: int,
    username: str,
    user_email: str,
    cafe_name: str,
    cafe_address: str,
    cafe_phone: str,
    table_descriptions: list[str],
    datetime_start_booking: 'datetime',
    datetime_finish_booking: 'datetime',
    upcomming_fl: bool,
    service_name: str = settings.title,
) -> None:
    """Уведомляет клиента о бронировании через Celery задачу.

    Args:
        self (Task): Экземпляр задачи.
        user_id (int): ID пользователя.
        username (str): Username пользователя.
        user_email (str): E-mail пользователя.
        cafe_name (str): Название кафе.
        cafe_address (str): Адрес кафе.
        cafe_phone (str): Телефон кафе.
        table_descriptions (list[str]): Описания столов.
        datetime_start_booking (datetime): ДатаВремя начала брони.
        datetime_finish_booking (datetime): ДатаВремя конец брони.
        service_name (str): Название сервиса.
        upcomming_fl (bool): Флаг напоминания. True, если это напоминание.

    """
    with contextualize_user(username=username, user_id=user_id):
        logger.info(
            'Отправка notify_client_booking | to={email} | cafe={cafe}',
            email=user_email,
            cafe=cafe_name,
        )
        html = (TEMPLATES_DIR / 'booking_confirmation.html').read_text(encoding='utf-8')
        start_booking = datetime_start_booking.strftime('%d.%m.%Y %H:%M')
        finish_booking = datetime_finish_booking.strftime('%d.%m.%Y %H:%M')
        table_descriptions_for_msg = '\n - '.join(table_descriptions)
        table_descriptions_html = ''.join(
            f'<li>{table_description}</li>' for table_description in table_descriptions
        )
        if upcomming_fl:
            action = 'Напоминание о бронировании.'
        else:
            action = 'Бронь подтверждена.'
        subject_msg = f'{service_name}: {action}'
        body_text_msg = (
            f'{action}.\n'
            f'Кафе: {cafe_name}\n'
            f'Столы:\n - {table_descriptions_for_msg}\n'
            f'Начало: {start_booking}\n'
            f'Конец: {finish_booking}\n'
            f'Адрес кафе: {cafe_address}\n'
            f'Телефон кафе: {cafe_phone}\n'
        )
        body_html_msg = html.format(
            action=action,
            service_name=service_name,
            username=username,
            cafe_name=cafe_name,
            cafe_address=cafe_address,
            cafe_phone=cafe_phone,
            table_descriptions=table_descriptions_html,
            start_booking=start_booking,
            finish_booking=finish_booking,
        )
        _send_email(
            to_addr=user_email,
            subject=subject_msg,
            body_text=body_text_msg,
            body_html=body_html_msg,
        )


@celery_app.task(
    name='notify_manager_booking',
    base=BaseTask,
    bind=True,
)
def notify_manager_booking(
    self: Task,
    user_id: int,
    username: str,
    user_email: str,
    user_phone: str,
    manager_cafe_email: str,
    cafe_name: str,
    table_descriptions: list[str],
    datetime_start_booking: 'datetime',
    datetime_finish_booking: 'datetime',
    booking_id: int,
    new_booking_fl: bool,
) -> None:
    """Уведомляет менеджера о бронировании через Celery задачу.

    Args:
        self (Task): Экземпляр задачи.
        user_id (int): ID пользователя.
        username (str): Username пользователя.
        user_email (str): E-mail пользователя.
        user_phone (str): Телефон пользователя.
        manager_cafe_email (str): E-mail администратора кафе.
        cafe_name (str): Название кафе.
        table_descriptions (list[str]): Описания столов.
        datetime_start_booking (datetime): ДатаВремя начала брони.
        datetime_finish_booking (datetime): ДатаВремя конец брони.
        booking_id (int): ID брони.
        new_booking_fl (bool): Флаг новой брони. True, если бронь новая.

    """
    with contextualize_user(username=username, user_id=user_id):
        logger.info(
            'Отправка notify_manager_booking | to={email} | cafe={cafe}',
            email=manager_cafe_email,
            cafe=cafe_name,
        )
        subject_msg = f'{cafe_name}: Бронь. ID: {booking_id}'
        start_booking = datetime_start_booking.strftime('%d.%m.%Y %H:%M')
        finish_booking = datetime_finish_booking.strftime('%d.%m.%Y %H:%M')
        table_descriptions_for_msg = '\n - '.join(table_descriptions)
        if new_booking_fl:
            body_text_msg = 'Новая бронь:'
        else:
            body_text_msg = 'Изменение брони:'
        body_text_msg += (
            f'\nКафе: {cafe_name}\n'
            f'Клиент: {username}\n'
            f'E-mail клиента: {user_email}\n'
            f'Телефон клиента: {user_phone}\n'
            f'ID брони: {booking_id}\n'
            f'Столы:\n - {table_descriptions_for_msg}\n'
            f'Начало: {start_booking}\n'
            f'Конец: {finish_booking}\n'
        )
        _send_email(
            to_addr=manager_cafe_email,
            subject=subject_msg,
            body_text=body_text_msg,
        )

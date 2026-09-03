"""Задачи с E-mail уведомлений."""

from datetime import datetime, timedelta, timezone
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
    from models.booking import Booking

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / 'templates'
NOTIFY_FOR_SECONDS = 60 * 60 * 3


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
        logger.debug('Начинаю отправку email через SMTP')
        try:
            _send_email(
                to_addr=user_email,
                subject=subject_msg,
                body_text=body_text_msg,
                body_html=body_html_msg,
            )
        except Exception as err:
            logger.error(
                'Ошибка отправки email | to={email} | error={error}',
                email=user_email,
                error=err,
            )
            raise

        logger.info('Email успешно отправлен | to={email}', email=user_email)


def notify_booking_handler(booking: 'Booking', new_fl: bool) -> None:
    """Обрабатывает логику уведомлений о бронировании.

    Args:
        booking (Booking): Объект брони.
        new_fl (bool): Новая бронь. True, если новая.

    """
    start_time = min([x.slot.start_time for x in booking.tables_slots])
    date_booking = booking.booking_date.strftime('%d.%m.%Y')
    start_time_booking_msg = start_time.strftime('%H:%M')
    notify_client_booking.delay(
        user_id=booking.user_id,
        username=booking.user.username,
        user_email=booking.user.email,
        cafe_name=booking.cafe.name,
        cafe_address=booking.cafe.address,
        cafe_phone=booking.cafe.phone,
        date_booking=date_booking,
        start_time_booking=start_time_booking_msg,
        number_of_guests=booking.guest_number,
        action='Бронь подтверждена',
    )
    for manager in booking.cafe.managers:
        notify_manager_booking.delay(
            user_id=booking.user_id,
            username=booking.user.username,
            user_email=booking.user.email,
            user_phone=booking.user.phone,
            manager_cafe_email=manager.email,
            cafe_name=booking.cafe.name,
            number_of_guests=booking.guest_number,
            date_booking=date_booking,
            start_time_booking=start_time_booking_msg,
            booking_id=booking.id,
            new_booking_fl=new_fl,
        )
    target_td = datetime.combine(booking.booking_date, start_time, tzinfo=timezone.utc)
    notify_dt = target_td - timedelta(seconds=NOTIFY_FOR_SECONDS)
    if datetime.now(timezone.utc) > notify_dt:
        return
    notify_client_booking.apply_async(
        eta=notify_dt,
        kwargs={
            'user_id': booking.user_id,
            'username': booking.user.username,
            'user_email': booking.user.email,
            'cafe_name': booking.cafe.name,
            'cafe_address': booking.cafe.address,
            'cafe_phone': booking.cafe.phone,
            'date_booking': date_booking,
            'start_time_booking': start_time_booking_msg,
            'number_of_guests': booking.guest_number,
            'action': 'Напоминание о бронировании',
        },
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
    number_of_guests: int,
    date_booking: str,
    start_time_booking: str,
    action: str,
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
        number_of_guests: (int): Число гостей.
        date_booking (str): Дата брони.
        start_time_booking (str): Время начало брони.
        service_name (str): Название сервиса.
        action (str): Название дейставия.

    """
    with contextualize_user(username=username, user_id=user_id):
        logger.info(
            'Отправка notify_client_booking | to={email} | cafe={cafe}',
            email=user_email,
            cafe=cafe_name,
        )
        html = (TEMPLATES_DIR / 'booking_confirmation.html').read_text(encoding='utf-8')
        subject_msg = f'{service_name}: {action}'
        body_text_msg = (
            f'{action}.\n'
            f'Кафе: {cafe_name}\n'
            f'Кол-во человек:\n - {number_of_guests}\n'
            f'Дата: {date_booking}\n'
            f'Начало: {start_time_booking}\n'
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
            number_of_guests=number_of_guests,
            date_booking=date_booking,
            start_time_booking=start_time_booking,
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
    number_of_guests: int,
    date_booking: str,
    start_time_booking: str,
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
        number_of_guests: (int): Число гостей.
        date_booking (str): Дата брони.
        start_time_booking (str): Время начало брони.
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
            f'Кол-во человек:\n - {number_of_guests}\n'
            f'Дата: {date_booking}\n'
            f'Начало: {start_time_booking}\n'
        )
        _send_email(
            to_addr=manager_cafe_email,
            subject=subject_msg,
            body_text=body_text_msg,
        )

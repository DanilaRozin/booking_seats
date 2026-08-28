"""Задачи с E-mail уведомлений."""

from pathlib import Path
from smtplib import (
    SMTPConnectError,
    SMTPDataError,
    SMTPHeloError,
    SMTPNotSupportedError,
    SMTPServerDisconnected,
)
from socket import gaierror
from socket import timeout as socket_timeout
from typing import TYPE_CHECKING, Any

from celery import Task
from loguru import logger

from services.send_email import _send_email

from core.celery_app import celery_app
from core.logging_config import contextualize_user, log_audit_event
from core.settings import settings

if TYPE_CHECKING:
    from datetime import date, time

    from celery.app.trace import TraceInfo

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / 'services' / 'templates'
MAX_RETRY_CELERY_EMAIL_TASK = 3
DEFAULT_RETRY_DELAY = 60


class CallbackTask(Task):
    """Базовая задача с автоматическим retry."""

    autoretry_for = (
        # Сетевые ошибки - retry
        OSError,
        gaierror,  # DNS resolution errors
        ConnectionError,
        socket_timeout,
        # SMTP временные ошибки - retry
        SMTPConnectError,
        SMTPServerDisconnected,
        SMTPHeloError,
        SMTPDataError,
        SMTPNotSupportedError,
    )
    # Максимальное кол-во попыток.
    retry_kwargs = {'max_retries': MAX_RETRY_CELERY_EMAIL_TASK}
    default_retry_delay = DEFAULT_RETRY_DELAY  # Задержка перед повтором.
    retry_backoff = True  # Экспоненциальная задержка.
    retry_jitter = True  # Случайная задержка.

    def on_retry(
        self,
        exc: Exception,
        task_id: str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        einfo: 'TraceInfo',
    ) -> None:
        """Логирует в случае повтора задачи."""
        logger.warning(
            'Retry задачи {task} | id={task_id} | попытка={retries}/{max} | ошибка={exc}',
            task=self.name,
            task_id=task_id,
            retries=self.request.retries,
            max=MAX_RETRY_CELERY_EMAIL_TASK,
            exc=exc,
        )
        return super().on_retry(exc, task_id, args, kwargs, einfo)

    def on_failure(
        self,
        exc: Exception,
        task_id: str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        einfo: 'TraceInfo',
    ) -> None:
        """Логирует в случае провала задачи."""
        logger.exception(
            'Задача {task} окончательно провалилась | id={task_id} | exc={exc}',
            task=self.name,
            task_id=task_id,
            exc=exc,
        )
        log_audit_event(
            'celery_task_failed',
            {'task': self.name, 'task_id': task_id, 'error': str(exc)},
            level='ERROR',
        )
        return super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_success(
        self,
        retval: Any,
        task_id: str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> None:
        """Логирует в случае успешного выполнения."""
        log_audit_event(
            'celery_task_success',
            {'task': self.name, 'task_id': task_id},
        )
        return super().on_success(retval, task_id, args, kwargs)


@celery_app.task(
    name='notify_registration',
    base=CallbackTask,
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
        subject_msg = f'{settings.title}: Регистрация пользователя {username}.'
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
    name='notify_booking',
    base=CallbackTask,
    bind=True,
)
def notify_booking(
    self: Task,
    user_id: int,
    username: str,
    user_email: str,
    cafe_name: str,
    table_number: int,
    date_booking: 'date',
    time_booking: 'time',
    service_name: str = settings.title,
) -> None:
    """Уведомляет о бронировании через Celery задачу.

    Args:
        self (Task): Экземпляр задачи.
        user_id (int): ID пользователя.
        username (str): Username пользователя.
        user_email (str): E-mail пользователя.
        cafe_name (str): Название кафе.
        table_number (int): Номер забронированного столика.
        date_booking (date): Дата брони.
        time_booking (time): Время брони.
        service_name (str): Название сервиса.

    """
    with contextualize_user(username=username, user_id=user_id):
        logger.info('Отправка notify_booking | to={email} | cafe={cafe}', email=user_email, cafe=cafe_name)
        html = (TEMPLATES_DIR / 'booking_confirmation.html').read_text(encoding='utf-8')
        subject_msg = f'{settings.title}: Уведомление о бронировании.'
        body_text_msg = ''
        body_html_msg = html.format(
            service_name=service_name,
            username=username,
            cafe_name=cafe_name,
            table_number=table_number,
            date_booking=date_booking.strftime('%d.%m.%Y'),
            time_booking=time_booking.strftime('%H:%M'),
        )
        _send_email(
            to_addr=user_email,
            subject=subject_msg,
            body_text=body_text_msg,
            body_html=body_html_msg,
        )

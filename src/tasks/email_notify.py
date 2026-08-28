"""Задачи с E-mail уведомлений."""

import asyncio
from pathlib import Path

from celery import Task

from services.send_email import _send_email

from core.celery_app import celery_app
from core.settings import settings

TEMPLATES_DIR = Path(__file__).parent / 'templates'
MAX_RETRY_CELERY_EMAIL_TASK = 3


class CallbackTask(Task):
    """Базовая задача с автоматическим retry."""

    autoretry_for = (  # Повторить при
        OSError,
    )
    # Максимальное кол-во попыток.
    retry_kwargs = {'max_retries': MAX_RETRY_CELERY_EMAIL_TASK}
    retry_backoff = True  # Экспоненциальная задержка.
    retry_jitter = True  # Случайная задержка.


@celery_app.task(
    name='notify_registration',
    base=CallbackTask,
)
def notify_registration(username: str, user_email: str) -> None:
    """Уведомляет о регистрации через Celery задачу.

    Args:
        username (str): Username пользователя.
        user_email (str): E-mail пользователя.

    """
    html = (TEMPLATES_DIR / 'registration.html').read_text(encoding='utf-8')
    subject_msg = f'{settings.title}: Регистрация пользователя {username}.'
    body_text_msg = f'Пользователь {username} зарегистрирован!'
    body_html_msg = html.format(text=body_text_msg)
    asyncio.run(
        _send_email(
            to_addr=user_email,
            subject=subject_msg,
            body_text=body_text_msg,
            body_html=body_html_msg,
        ),
    )


@celery_app.task(
    name='notify_booking',
    base=CallbackTask,
)
def notify_booking(user_email: str) -> None:
    """Уведомляет о бронировании через Celery задачу."""
    html = (TEMPLATES_DIR / 'booking_confirmation.html').read_text(encoding='utf-8')
    subject_msg = f'{settings.title}: Уведомление о бронировании.'
    body_text_msg = ''
    body_html_msg = html.format()
    asyncio.run(
        _send_email(
            to_addr=user_email,
            subject=subject_msg,
            body_text=body_text_msg,
            body_html=body_html_msg,
        ),
    )

"""Конфигурация Celery приложения."""

from typing import Any

from celery import Celery
from celery.signals import setup_logging

from core.settings import settings


@setup_logging.connect
def setup_celery_logging(*args: Any, **kwargs: Any) -> None:
    """Подключаем Loguru, отключая стандартное логирование Celery."""
    from core.logging_config import configure_logging

    configure_logging()


celery_app = Celery(
    'booking_seats',
    broker=settings.rabbitmq.celery_broker_url,
    backend=settings.redis.celery_backend_url,
    include=[
        'tasks.email_notify',
    ],
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_max_tasks_per_child=1_000,
    worker_send_task_events=True,
    task_send_sent_event=True,
)

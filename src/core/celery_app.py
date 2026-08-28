"""Конфигурация Celery приложения."""

from celery import Celery

from core.settings import settings

celery_app = Celery(
    'tg_bot_tasks',
    broker=settings.rabbitmq.celery_broker_url,
    backend=settings.redis.celery_backend_url,
    include=[
        '',
    ],
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=60 * 5,
    task_acks_late=True,
    worker_max_tasks_per_child=1_000,
    worker_send_task_events=True,
    task_send_sent_event=True,
)

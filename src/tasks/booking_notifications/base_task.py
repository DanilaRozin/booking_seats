"""Определение базовой Задачи."""

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

from core.logging_config import log_audit_event

if TYPE_CHECKING:
    from celery.app.trace import TraceInfo

MAX_RETRY_CELERY_EMAIL_TASK = 3
DEFAULT_RETRY_DELAY = 60


class BaseTask(Task):
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

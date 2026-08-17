import json
import sys
from pathlib import Path
from typing import Any, Mapping, Optional

from loguru import logger

SYSTEM_USERNAME = 'SYSTEM'
SYSTEM_USER_ID = '-1'

LOG_FORMAT = (
    '<green>{time:YYYY-MM-DD HH:mm:ss}</green> | '
    '<level>{level: <8}</level> | '
    'user=<cyan>{extra[username]}</cyan>:<cyan>{extra[user_id]}</cyan> | '
    '{message}'
)


def configure_logging(
    log_dir: str = 'logs',
    level: str = 'INFO',
    rotation: str = '00:00',
    retention: int = 10,
    enqueue: bool = True,
) -> None:
    """Настраивает логирование через loguru.

    Параметры:
        log_dir: директория для хранения логов;
        level: минимальный уровень логирования;
        rotation: расписание ротации лог-файла;
        retention: количество хранимых ротированных файлов;
        enqueue: использовать внутреннюю очередь для потокобезопасности.
    """
    logger.remove()

    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    logger.add(
        sys.stdout,
        level=level.upper(),
        format=LOG_FORMAT,
        enqueue=enqueue,
        backtrace=False,
        diagnose=False,
    )

    file_path = log_path / 'app.log'
    logger.add(
        file_path,
        level=level.upper(),
        format=LOG_FORMAT,
        rotation=rotation,
        retention=retention,
        enqueue=enqueue,
        backtrace=False,
        diagnose=False,
        encoding='utf-8',
    )

    logger.configure(
        extra={
            'username': SYSTEM_USERNAME,
            'user_id': SYSTEM_USER_ID,
        },
    )


def contextualize_user(
    user_id: Optional[int | str] = None,
    username: Optional[str] = None,
) -> Any:
    """Возвращает контекстный менеджер для временной подстановки user_id

    и username.

    Если значения не переданы, используются системные значения по умолчанию.
    """
    resolved_user_id = str(user_id) if user_id is not None else SYSTEM_USER_ID
    resolved_username = username or SYSTEM_USERNAME

    return logger.contextualize(
        username=resolved_username,
        user_id=resolved_user_id,
    )


def log_audit_event(
    event: str,
    details: Optional[Mapping[str, Any]] = None,
    level: str = 'INFO',
) -> None:
    """Записывает аудит-событие в лог с JSON-деталями.

    Детали события сериализуются в JSON и добавляются к сообщению.
    """
    serialized_details = json.dumps(
        details or {},
        ensure_ascii=False,
        default=str,
        sort_keys=True,
    )
    logger.log(
        level.upper(),
        '{event} | details={details}',
        event=event,
        details=serialized_details,
    )

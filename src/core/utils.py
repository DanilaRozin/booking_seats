from datetime import datetime, timezone


def utcnow_naive() -> datetime:
    """Возвращает текущее время."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

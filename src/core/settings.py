import os
from pathlib import Path

from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
_env_file = Path(os.getenv('ENV_FILE', PROJECT_ROOT / 'infra' / '.env'))


class RabbitMQConfig(BaseModel):
    """Конфигурация RabbitMQ."""

    user: str
    password: SecretStr
    host: str
    port: int
    vhost: str

    @property
    def celery_broker_url(self) -> str:
        """Конкатенирует URL Celery backend."""
        return f'amqp://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.vhost}'


class RedisConfig(BaseModel):
    """Конфигурация Redis."""

    host: str
    port: int
    db_celery_backend: int
    db_cache: int
    password: SecretStr | None = None

    @property
    def celery_backend_url(self) -> str:
        """Конкатенирует URL Celery backend."""
        auth = f':{self.password.get_secret_value()}@' if self.password else ''
        return f'redis://{auth}{self.host}:{self.port}/{self.db_celery_backend}'

    @property
    def fastapi_cache_url(self) -> str:
        """Конкатенирует URL Celery backend."""
        auth = f':{self.password.get_secret_value()}@' if self.password else ''
        return f'redis://{auth}{self.host}:{self.port}/{self.db_cache}'


class SMTPConfig(BaseModel):
    """Конфигурация SMTP."""

    host: str
    port: int
    login: str
    password: SecretStr


class PostgresConfig(BaseModel):
    """Конфигурация POSTGRES."""

    server: str
    port: int
    user: str
    password: SecretStr
    db: str

    @property
    def url(self) -> str:
        """Конкатенирует URL БД."""
        return (
            f'postgresql+asyncpg://{self.user}:{self.password.get_secret_value()}@'
            f'{self.server}:{self.port}/{self.db}'
        )


class Settings(BaseSettings):
    """Настройки приложения."""

    model_config = SettingsConfigDict(
        env_file=_env_file,
        env_nested_delimiter='__',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    title: str = 'Booking Seats'
    version: str = '0.0.1'
    description: str = (
        'Сервис бронирования мест в кафе: управление пользователями, '
        'кафе, столами, слотами, блюдами и акциями. '
        'Асинхронный REST API на FastAPI с фоновой рассылкой уведомлений '
        'через Celery + RabbitMQ, кэшированием на Redis и хранением данных '
        'в PostgreSQL.'
    )

    secret: SecretStr

    postgres: PostgresConfig
    rabbitmq: RabbitMQConfig
    redis: RedisConfig
    smtp: SMTPConfig


settings = Settings()

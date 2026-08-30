import os
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
_env_file = Path(os.getenv('ENV_FILE', PROJECT_ROOT / 'infra' / '.env'))


def settings_config(env_prefix: str = '') -> SettingsConfigDict:
    """Возвращает единый config для pydantic-settings.

    Args:
        env_prefix (str): Префикс для значений в env.

    Returns:
        SettingsConfigDict: Настройки класса.

    """
    return SettingsConfigDict(
        env_file=_env_file,
        env_prefix=env_prefix,
        env_file_encoding='utf-8',
        extra='ignore',
    )


class RabbitMQConfig(BaseSettings):
    """Конфигурация RabbitMQ."""

    model_config = settings_config(env_prefix='RABBITMQ__')

    user: str
    password: SecretStr
    host: str
    port: int
    vhost: str

    @property
    def celery_broker_url(self) -> str:
        """Конкатенирует URL Celery backend."""
        return f'amqp://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.vhost}'


class RedisConfig(BaseSettings):
    """Конфигурация Redis."""

    model_config = settings_config(env_prefix='REDIS__')

    host: str
    port: int
    db_celery_backend: int

    @property
    def celery_backend_url(self) -> str:
        """Конкатенирует URL Celery backend."""
        return f'redis://{self.host}:{self.port}/{self.db_celery_backend}'


class SMTPConfig(BaseSettings):
    """Конфигурация SMTP."""

    model_config = settings_config(env_prefix='SMTP__')

    host: str
    port: int
    login: str
    password: SecretStr


class POSTGRESConfig(BaseSettings):
    """Конфигурация POSTGRES."""

    model_config = settings_config(env_prefix='POSTGRES__')

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

    model_config = settings_config()

    # Общие настройки
    title: str = 'Booking Seats'
    version: str = '0.0.1'
    description: str = 'Основа для приложения'

    # Настройки для FastAPI users
    secret: SecretStr

    postgres: POSTGRESConfig = Field(default_factory=POSTGRESConfig)
    rabbitmq: RabbitMQConfig = Field(default_factory=RabbitMQConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    smtp: SMTPConfig = Field(default_factory=SMTPConfig)


settings = Settings()

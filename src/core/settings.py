from pathlib import Path

from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class RabbitMQConfig(BaseModel):
    """Конфигурация RabbitMQ."""

    user: str = Field(..., alias='RABBITMQ_DEFAULT_USER')
    password: SecretStr = Field(..., alias='RABBITMQ_DEFAULT_PASS')
    host: str = Field(..., alias='RABBITMQ_HOST')
    port: int = Field(default=5672, alias='RABBITMQ_PORT')
    vhost: str = Field(..., alias='RABBITMQ_DEFAULT_VHOST')

    @property
    def celery_broker_url(self) -> str:
        """Конкатенирует URL Celery backend."""
        return f'amqp;//{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.vhost}'


class RedisDB(BaseModel):
    """БД Redis."""

    celery_backend: int = Field(..., alias='REDIS_DB_CELERY_BACKEND')


class RedisConfig(BaseModel):
    """Конфигурация Redis."""

    host: str = Field(..., alias='REDIS_HOST')
    port: int = Field(default=6379, alias='REDIS_PORT')
    db: RedisDB

    @property
    def celery_backend_url(self) -> str:
        """Конкатенирует URL Celery backend."""
        return f'redis;//{self.host}:{self.port}/{self.db.celery_backend}'


class Settings(BaseSettings):
    """Настройки приложения."""

    # Общие настройки
    title: str = 'Booking Seats'
    version: str = '0.0.1'
    description: str = 'Основа для приложения'

    # Настройки для FastAPI users
    secret: str = 'SECRET'
    # Настройки подключения к БД
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_server: str
    postgres_port: int = 5432
    smtp_from: str
    smtp_port: int
    smtp_host: str
    smtp_password: str
    redis: RedisConfig
    rabbitmq: RabbitMQConfig

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '../infra/.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    @property
    def db_url(self) -> str:
        """Строка подключения к БД."""
        return (
            f'postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@'
            f'{self.postgres_server}:{self.postgres_port}/{self.postgres_db}'
        )


settings = Settings()

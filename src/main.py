from contextlib import asynccontextmanager  # Ruff
from typing import AsyncGenerator

import uvicorn
from fastapi import Depends, FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from api.routers import main_router, tags
from middleware.logging_context import logging_context_dependency, request_logging_middleware

from core.exception_handlers import register_exception_handlers
from core.logging_config import configure_logging
from core.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Жизненный цикл приложения FastAPI."""
    # TODO: Добавить код, выполняемый при старте приложения
    redis = aioredis.from_url(settings.redis.fastapi_cache_url)
    FastAPICache.init(RedisBackend(redis), prefix='fastapi-cache')
    yield
    # TODO: Добавить код, выполняемый при остановке приложения
    await redis.close()


app = FastAPI(
    title=settings.title,
    version=settings.version,
    description=settings.description,
    lifespan=lifespan,
    openapi_tags=tags.tag_list,
    dependencies=[Depends(logging_context_dependency)],
)
register_exception_handlers(app)


configure_logging(
    log_dir='logs',
    level='INFO',
    rotation='00:00',
    retention=10,
)

app.middleware('http')(request_logging_middleware)


@app.get('/', response_model=dict)
async def index() -> dict:
    """Основная страница."""
    return {
        'app': f'{settings.title} ({settings.version})',
        'description': settings.description,
        'status': 'OK',
    }


app.include_router(main_router)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)

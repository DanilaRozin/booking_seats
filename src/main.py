import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI

from api.v1.media import router as media_router

from src.api.routers import main_router
from src.core.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Жизненный цикл приложения FastAPI."""
    # TODO: Добавить код, выполняемый при старте приложения
    yield
    # TODO: Добавить код, выполняемый при остановке приложения


app = FastAPI(
    title=settings.title,
    version=settings.version,
    description=settings.description,
)

app.include_router(media_router, prefix="/api/v1")


@app.get(
    path='/',
    response_model=dict,
)
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

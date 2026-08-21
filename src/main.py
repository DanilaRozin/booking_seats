from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from api.routers import main_router, tags
from middleware.logging_context import logging_context_middleware

from core.logging_config import configure_logging
from core.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI
                   ) -> AsyncGenerator:
    """Жизненный цикл приложения FastAPI."""
    # TODO: Добавить код, выполняемый при старте приложения
    yield
    # TODO: Добавить код, выполняемый при остановке приложения


configure_logging(
    log_dir="logs",
    level="INFO",
    rotation="00:00",
    retention=10,
)

app = FastAPI(
    title=settings.title,
    version=settings.version,
    description=settings.description,
    openapi_tags=tags.tag_list,
)

app.middleware("http")(logging_context_middleware)
app.include_router(main_router)


@app.get("/", response_model=dict)
async def index() -> dict:
    """Главная страница API: возвращает метаданные приложения и статус."""
    return {
        "app": f"{settings.title} ({settings.version})",
        "description": settings.description,
        "status": "OK",
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException
                                 ) -> JSONResponse:
    """Возращает ошибки в формате {"message":...}."""
    return JSONResponse(
        status_code=exc.status_code,
        content={'message': exc.detail},
    )


app.include_router(main_router)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)

from uuid import UUID
from fastapi import APIRouter, File, UploadFile, status
from fastapi.responses import FileResponse

from schemas.media import MediaResponse
from services.media import MediaService

router = APIRouter(prefix="/media", tags=["Media (Изображения)"])


@router.post(
    "/",
    response_model=MediaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Загрузить изображение",
    description="Принимает файл (JPG/PNG до 5МБ), оптимизирует его через Pillow и сохраняет.",
)
async def upload_media(file: UploadFile = File(...)) -> MediaResponse:
    result = await MediaService.save_image(file)
    return MediaResponse(**result)


@router.get(
    "/{media_id}",
    response_class=FileResponse,
    summary="Получить изображение",
    description="Возвращает файл изображения по его UUID.",
)
async def get_media(media_id: UUID) -> FileResponse:
    file_path = MediaService.get_image_path(media_id)
    return FileResponse(path=file_path, media_type="image/jpeg")

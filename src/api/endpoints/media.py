from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import FileResponse

from schemas.media import MediaResponse
from services.media import MediaService

from core.user import current_manager_without_cafe

router = APIRouter()


@router.post(
    '/',
    response_model=MediaResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Загрузить изображение',
    dependencies=[Depends(current_manager_without_cafe)],
)
async def upload_media(file: UploadFile = File(...)) -> MediaResponse:
    """Принимает файл (JPG/PNG до 5МБ) и сохраняет."""
    result = await MediaService.save_image(file)
    return MediaResponse(**result)


@router.get(
    '/{media_id}',
    response_class=FileResponse,
    summary='Получить изображение',
)
async def get_media(media_id: UUID) -> FileResponse:
    """Возвращает файл изображения по его UUID."""
    file_path = MediaService.get_image_path(media_id)
    return FileResponse(path=file_path, media_type='image/jpeg')

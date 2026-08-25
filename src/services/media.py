import uuid
from pathlib import Path

from PIL import Image, UnidentifiedImageError
from fastapi import HTTPException, UploadFile, status

from core.constants import ALLOWED_CONTENT_TYPES, MAX_FILE_SIZE, UPLOAD_DIR

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class MediaService:
    """Сервис обработки и сохранения изображений."""

    @staticmethod
    async def save_image(file: UploadFile) -> dict:
        """Валидирует и сохраняет изображение."""
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            allowed_str = ', '.join(mime.split('/')[-1].upper() for mime in ALLOWED_CONTENT_TYPES)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Неподдерживаемый формат файла. Разрешены: {allowed_str}',
            )

        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            max_mb = int(MAX_FILE_SIZE / (1024 * 1024))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Размер файла превышает допустимый лимит в {max_mb} МБ.',
            )

        media_id = uuid.uuid4()
        extension = '.jpg'
        filename = f'{media_id}{extension}'
        file_path = UPLOAD_DIR / filename

        try:
            await file.seek(0)
            with Image.open(file.file) as image:
                if image.mode in ('RGBA', 'P'):
                    image = image.convert('RGB')

                image.save(file_path, 'JPEG', quality=85)
        except UnidentifiedImageError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Загруженный файл не является валидным изображением.',
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Ошибка при обработке изображения: {str(e)}',
            )

        return {
            'id': media_id,
            'filename': filename,
            'content_type': 'image/jpeg',
        }

    @staticmethod
    def get_image_path(media_id: uuid.UUID) -> Path:
        """Возвращает путь к файлу по его UUID."""
        filename = f'{media_id}.jpg'
        file_path = UPLOAD_DIR / filename

        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Изображение не найдено.',
            )

        return file_path

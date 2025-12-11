from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.repositories.document import DocumentRepository
from app.core.config import settings
from app.core.storage import save_file


class DocumentService:
    def __init__(self, session: AsyncSession):
        self.repo = DocumentRepository(session)

    async def upload(
        self,
        *,
        file_obj,
        filename: str,
        mime_type: str,
        user_id: int | None,
        donation_id: int | None,
        event_id: int | None,
        description: str | None,
        is_public: bool,
    ):
        try:
            stored_path, size_bytes, checksum = save_file(
                file_obj=file_obj,
                filename=filename,
                mime_type=mime_type,
                max_size_bytes=settings.max_upload_mb * 1024 * 1024,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        doc = await self.repo.create(
            file_name=filename,
            stored_path=stored_path,
            mime_type=mime_type,
            size_bytes=size_bytes,
            checksum=checksum,
            description=description,
            is_public=is_public,
            user_id=user_id,
            donation_id=donation_id,
            event_id=event_id,
        )
        return doc

    async def get(self, doc_id: int):
        doc = await self.repo.get(doc_id)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado")
        return doc

    async def list_all(self):
        return await self.repo.list_all()

    async def list_by_user(self, user_id: int):
        return await self.repo.list_by_user(user_id)


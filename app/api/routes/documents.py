from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse

from app.api.schemas import DocumentRead
from app.api.services.document import DocumentService
from app.core.deps import get_current_user, require_admin
from app.db.session import get_session
from app.models.user import User

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentRead, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    link_type: str | None = Form(None),
    ref_id: int | None = Form(None),
    description: str | None = Form(None),
    is_public: bool = Form(False),
    session=Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    donation_id = ref_id if link_type == "donation" else None
    user_id = ref_id if link_type == "user" else current_user.id
    event_id = ref_id if link_type == "event" else None

    service = DocumentService(session)
    doc = await service.upload(
        file_obj=file.file,
        filename=file.filename,
        mime_type=file.content_type or "",
        user_id=user_id,
        donation_id=donation_id,
        event_id=event_id,
        description=description,
        is_public=is_public,
    )
    return doc


@router.get("/{doc_id}")
async def download_document(
    doc_id: int,
    session=Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    service = DocumentService(session)
    doc = await service.get(doc_id)

    # Autorización básica
    if not doc.is_public:
        is_owner = doc.user_id == current_user.id
        is_admin = current_user.role == "admin"
        if not (is_owner or is_admin):
            raise HTTPException(status_code=403, detail="No autorizado para acceder a este documento")

    path = Path(doc.stored_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado en almacenamiento")

    return FileResponse(path, media_type=doc.mime_type, filename=doc.file_name)


@router.get("", response_model=list[DocumentRead], dependencies=[Depends(require_admin)])
async def list_documents(session=Depends(get_session)):
    service = DocumentService(session)
    return await service.list_all()


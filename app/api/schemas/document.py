from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DocumentCreate(BaseModel):
    link_type: str | None = None  # donation|user|event
    ref_id: int | None = None
    description: str | None = None
    is_public: bool = False


class DocumentRead(BaseModel):
    id: int
    file_name: str
    mime_type: str
    size_bytes: int
    checksum: str | None
    description: str | None
    is_public: bool
    uploaded_at: datetime
    donation_id: int | None = None
    user_id: int | None = None
    event_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


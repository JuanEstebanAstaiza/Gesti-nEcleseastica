import os
import uuid
import hashlib
from pathlib import Path
from typing import BinaryIO

from app.core.config import settings


ALLOWED_MIME = {"application/pdf", "image/png", "image/jpeg"}


def ensure_storage_dir() -> Path:
    path = Path(settings.storage_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_file(file_obj: BinaryIO, filename: str, mime_type: str, max_size_bytes: int) -> tuple[str, int, str]:
    if mime_type not in ALLOWED_MIME:
        raise ValueError("Tipo de archivo no permitido")

    storage_dir = ensure_storage_dir()
    token = uuid.uuid4().hex
    stored_name = f"{token}_{filename}"
    stored_path = storage_dir / stored_name

    hasher = hashlib.sha256()
    size = 0

    with open(stored_path, "wb") as dest:
        chunk = file_obj.read(8192)
        while chunk:
            size += len(chunk)
            if size > max_size_bytes:
                dest.close()
                stored_path.unlink(missing_ok=True)
                raise ValueError("Archivo excede el tamaño máximo permitido")
            hasher.update(chunk)
            dest.write(chunk)
            chunk = file_obj.read(8192)

    checksum = hasher.hexdigest()
    return str(stored_path), size, checksum


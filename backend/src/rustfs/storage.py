from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from src.core.config import get_settings
from src.rustfs.client import ensure_bucket, get_rustfs_client


@dataclass
class RustFSFileInfo:
    bucket: str
    object_key: str
    filename: str
    content_type: str | None
    size: int | None


def build_object_key(filename: str, object_prefix: str) -> str:
    suffix = Path(filename).suffix.lower()
    return f"{object_prefix}/{uuid4().hex}{suffix}"


def upload_file_to_rustfs(
    file: UploadFile,
    object_prefix: str,
    object_key: str | None = None,
) -> RustFSFileInfo:
    settings = get_settings()
    client = get_rustfs_client()

    ensure_bucket(client, settings)

    filename = file.filename or "file"
    object_key = object_key or build_object_key(filename, object_prefix)
    extra_args = {"ContentType": file.content_type} if file.content_type else None
    client.upload_fileobj(
        file.file,
        settings.rustfs_bucket,
        object_key,
        ExtraArgs=extra_args,
    )

    return RustFSFileInfo(
        bucket=settings.rustfs_bucket,
        object_key=object_key,
        filename=filename,
        content_type=file.content_type,
        size=file.size,
    )

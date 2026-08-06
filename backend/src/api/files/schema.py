from pydantic import BaseModel


class UploadFileResponse(BaseModel):
    object_key: str
    url: str
    processed_object_key: str | None = None
    processed_url: str | None = None

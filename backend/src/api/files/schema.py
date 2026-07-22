from pydantic import BaseModel


class UploadFileResponse(BaseModel):
    object_key: str
    url: str

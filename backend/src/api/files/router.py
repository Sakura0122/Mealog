from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile

from src.api.files.schema import UploadFileResponse
from src.api.files.service import UploadType, upload_file
from src.common.result import Result
from src.rustfs.url import build_public_file_url

router = APIRouter(prefix="/files", tags=["文件"])


@router.post(
    "/upload",
    summary="上传文件",
    description="上传用户文件到对象存储，并返回对象存储键和公开访问地址。",
    response_model=Result[UploadFileResponse],
)
def upload_user_file(
    file: Annotated[UploadFile, File(description="需要上传的文件")],
    upload_type: Annotated[
        UploadType,
        Form(alias="type", description="文件分类：avatar、images 或 files"),
    ],
) -> Result[UploadFileResponse]:
    file_info = upload_file(file, upload_type)
    return Result.success(
        UploadFileResponse(
            object_key=file_info.object_key,
            url=build_public_file_url(file_info.object_key),
        )
    )

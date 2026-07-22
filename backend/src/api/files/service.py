from typing import Literal

from fastapi import UploadFile

from src.common.exceptions import BusinessException
from src.common.result_code import ResultCodeEnum
from src.core.config import get_settings
from src.rustfs.storage import RustFSFileInfo, upload_file_to_rustfs

UploadType = Literal["avatar", "images", "files"]


def upload_file(file: UploadFile, upload_type: UploadType) -> RustFSFileInfo:
    settings = get_settings()
    if file.size is None:
        raise BusinessException(ResultCodeEnum.PARAM_ERROR, "无法确定上传文件大小")
    if file.size > settings.file_upload_max_size:
        raise BusinessException(ResultCodeEnum.PARAM_ERROR, "上传文件大小超过限制")

    return upload_file_to_rustfs(file, f"uploads/user/{upload_type}")

from io import BytesIO
from typing import Literal
from uuid import UUID

from fastapi import UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError
from starlette.datastructures import Headers

from src.common.exceptions import BusinessException
from src.common.result_code import ResultCodeEnum
from src.core.config import get_settings
from src.rustfs.storage import RustFSFileInfo, upload_file_to_rustfs

UploadType = Literal["avatar", "images", "files"]
IMAGE_QUALITY = 80
IMAGE_MAX_SIZE = {"avatar": 512, "images": 1600}


def compress_image(file: UploadFile, max_size: int) -> UploadFile:
    try:
        with Image.open(file.file) as source_image:
            # 修正手机照片方向后统一转成 JPEG，避免不同图片格式产生不同压缩结果。
            image = ImageOps.exif_transpose(source_image).convert("RGB")
    except Image.DecompressionBombError, UnidentifiedImageError, OSError, ValueError:
        raise BusinessException(ResultCodeEnum.PARAM_ERROR, "上传文件不是有效图片") from None

    output = BytesIO()
    # 按最长边等比缩小，thumbnail 不会放大小尺寸图片。
    image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    image.save(output, format="JPEG", quality=IMAGE_QUALITY, optimize=True)
    image.close()
    size = output.tell()
    output.seek(0)
    return UploadFile(
        file=output,
        size=size,
        filename="image.jpg",
        headers=Headers({"content-type": "image/jpeg"}),
    )


def upload_file(file: UploadFile, upload_type: UploadType, user_id: UUID) -> RustFSFileInfo:
    settings = get_settings()
    if file.size is None:
        raise BusinessException(ResultCodeEnum.PARAM_ERROR, "无法确定上传文件大小")
    if file.size > settings.file_upload_max_size:
        raise BusinessException(ResultCodeEnum.PARAM_ERROR, "上传文件大小超过限制")

    max_size = IMAGE_MAX_SIZE.get(upload_type)
    upload_target = compress_image(file, max_size) if max_size is not None else file
    try:
        # 用户 ID 取自登录态，确保对象目录不能由客户端伪造。
        return upload_file_to_rustfs(upload_target, f"uploads/user/{user_id}/{upload_type}")
    finally:
        if upload_target is not file:
            upload_target.file.close()

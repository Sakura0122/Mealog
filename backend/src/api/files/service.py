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
from src.rustfs.url import build_thumbnail_object_key

UploadType = Literal["avatar", "images", "files"]
IMAGE_QUALITY = 80
IMAGE_MAX_SIZE = {"avatar": 512, "images": 1600}
THUMBNAIL_MAX_SIZE = 480
THUMBNAIL_QUALITY = 75


def _build_image_file(image: Image.Image, max_size: int, quality: int) -> UploadFile:
    resized_image = image.copy()
    # 按最长边等比缩小，thumbnail 不会放大小尺寸图片。
    resized_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    output = BytesIO()
    resized_image.save(output, format="JPEG", quality=quality, optimize=True)
    resized_image.close()
    size = output.tell()
    output.seek(0)
    return UploadFile(
        file=output,
        size=size,
        filename="image.jpg",
        headers=Headers({"content-type": "image/jpeg"}),
    )


def compress_image(
    file: UploadFile,
    max_size: int,
    generate_thumbnail: bool,
) -> tuple[UploadFile, UploadFile | None]:
    try:
        with Image.open(file.file) as source_image:
            # 修正手机照片方向后统一转成 JPEG，避免不同图片格式产生不同压缩结果。
            image = ImageOps.exif_transpose(source_image).convert("RGB")
    except Image.DecompressionBombError, UnidentifiedImageError, OSError, ValueError:
        raise BusinessException(ResultCodeEnum.PARAM_ERROR, "上传文件不是有效图片") from None

    upload_image = _build_image_file(image, max_size, IMAGE_QUALITY)
    thumbnail = (
        _build_image_file(image, THUMBNAIL_MAX_SIZE, THUMBNAIL_QUALITY)
        if generate_thumbnail
        else None
    )
    image.close()
    return upload_image, thumbnail


def upload_file(
    file: UploadFile,
    upload_type: UploadType,
    user_id: UUID,
    generate_thumbnail: bool = False,
) -> tuple[RustFSFileInfo, RustFSFileInfo | None]:
    settings = get_settings()
    if file.size is None:
        raise BusinessException(ResultCodeEnum.PARAM_ERROR, "无法确定上传文件大小")
    if file.size > settings.file_upload_max_size:
        raise BusinessException(ResultCodeEnum.PARAM_ERROR, "上传文件大小超过限制")

    max_size = IMAGE_MAX_SIZE.get(upload_type)
    should_generate_thumbnail = generate_thumbnail and upload_type == "images"
    if max_size is not None:
        upload_target, thumbnail_target = compress_image(
            file,
            max_size,
            should_generate_thumbnail,
        )
    else:
        upload_target, thumbnail_target = file, None
    try:
        # 用户 ID 取自登录态，确保对象目录不能由客户端伪造。
        file_info = upload_file_to_rustfs(
            upload_target,
            f"uploads/user/{user_id}/{upload_type}",
        )
        thumbnail_info = (
            _upload_thumbnail(
                thumbnail_target,
                file_info.object_key,
                user_id,
            )
            if thumbnail_target is not None
            else None
        )
        return file_info, thumbnail_info
    finally:
        if upload_target is not file:
            upload_target.file.close()
        if thumbnail_target is not None:
            thumbnail_target.file.close()


def _upload_thumbnail(
    thumbnail: UploadFile,
    original_object_key: str,
    user_id: UUID,
) -> RustFSFileInfo:
    """以原图文件名派生缩略图 key，避免将缩略图 key 写入业务表。"""

    thumbnail_object_key = build_thumbnail_object_key(original_object_key)
    if thumbnail_object_key is None:
        raise BusinessException(ResultCodeEnum.PARAM_ERROR, "无法生成图片缩略图路径")
    return upload_file_to_rustfs(
        thumbnail,
        f"uploads/user/{user_id}/thumbnails",
        object_key=thumbnail_object_key,
    )

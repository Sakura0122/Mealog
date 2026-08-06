from urllib.parse import quote

from src.core.config import get_settings


def build_public_file_url(object_key: str) -> str:
    """
    构建公共文件 URL。

    :param object_key: 对象键。
    :return: 公共文件 URL。
    """
    base_url = get_settings().rustfs_public_base_url.rstrip("/")
    return f"{base_url}/{quote(object_key, safe='/')}"


def build_thumbnail_object_key(object_key: str) -> str | None:
    """按图片对象路径约定派生缩略图对象键。"""

    marker = "/images/"
    if marker not in object_key:
        return None
    return object_key.replace(marker, "/thumbnails/", 1)

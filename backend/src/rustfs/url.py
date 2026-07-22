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

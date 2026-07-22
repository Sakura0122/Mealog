from functools import lru_cache
from pathlib import Path

from pydantic import PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict

# 固定到 backend 目录，避免从不同目录启动服务时读错 .env。
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """配置类，用于读取 .env 文件中的配置。"""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    database_url: str | None = None
    database_echo: bool = False
    logger_level: str = "INFO"
    logger_dir: Path = BASE_DIR / "logs"

    wechat_app_id: str | None = None
    wechat_app_secret: str | None = None
    auth_token_secret: str | None = None
    auth_token_expire_seconds: int = 60 * 60 * 24 * 30
    admin_token_secret: str | None = None
    admin_token_expire_seconds: int = 60 * 60 * 8
    cors_allow_origins: str = "*"
    file_upload_max_size: PositiveInt = 10 * 1024 * 1024

    rustfs_endpoint_url: str = ""
    rustfs_access_key: str = ""
    rustfs_secret_key: str = ""
    rustfs_bucket: str = ""
    rustfs_public_base_url: str = ""


@lru_cache
def get_settings() -> Settings:
    # 配置在服务运行期间保持不变，缓存后避免每次请求都重新读取 .env。
    return Settings()


settings = get_settings()

from functools import lru_cache
from typing import Any, Protocol, cast

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from src.core.config import Settings, get_settings


class RustFSS3Client(Protocol):
    def head_bucket(self, **kwargs: Any) -> Any: ...

    def create_bucket(self, **kwargs: Any) -> Any: ...

    def upload_fileobj(self, fileobj: Any, bucket: str, key: str, **kwargs: Any) -> Any: ...


@lru_cache
def get_rustfs_client() -> RustFSS3Client:
    settings = get_settings()
    return cast(
        RustFSS3Client,
        boto3.client(
            "s3",
            endpoint_url=settings.rustfs_endpoint_url,
            aws_access_key_id=settings.rustfs_access_key,
            aws_secret_access_key=settings.rustfs_secret_key,
            config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
            region_name="us-east-1",
        ),
    )


def ensure_bucket(client: RustFSS3Client, settings: Settings) -> None:
    try:
        client.head_bucket(Bucket=settings.rustfs_bucket)
    except ClientError as error:
        error_code = error.response.get("Error", {}).get("Code")
        if error_code not in {"404", "NoSuchBucket"}:
            raise

        client.create_bucket(Bucket=settings.rustfs_bucket)

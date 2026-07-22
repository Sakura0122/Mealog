from datetime import UTC, datetime, timedelta
from typing import Literal
from uuid import UUID

import jwt
from jwt import InvalidTokenError

from src.common.exceptions import BusinessException
from src.common.result_code import ResultCodeEnum
from src.core.config import get_settings

_ALGORITHM = "HS256"
_ACCESS_TOKEN_TYPE = "user"
_ADMIN_TOKEN_TYPE = "admin"
_ACCESS_TOKEN_AUDIENCE = "mealog-user"
_ADMIN_TOKEN_AUDIENCE = "mealog-admin"

TokenType = Literal["user", "admin"]


def _require_secret(secret: str | None, name: str) -> str:
    if not secret:
        raise BusinessException(ResultCodeEnum.SYSTEM_ERROR, f"{name} 未配置")

    return secret


def _create_token(
    subject: UUID,
    *,
    secret: str,
    expire_seconds: int,
    token_type: TokenType,
    audience: str,
) -> str:
    expires_at = datetime.now(UTC) + timedelta(seconds=expire_seconds)
    return jwt.encode(
        {
            "sub": str(subject),
            "token_type": token_type,
            "aud": audience,
            "exp": expires_at,
        },
        secret,
        algorithm=_ALGORITHM,
    )


def _parse_token(
    token: str,
    *,
    secret: str,
    token_type: TokenType,
    audience: str,
) -> UUID:
    try:
        data = jwt.decode(
            token,
            secret,
            algorithms=[_ALGORITHM],
            audience=audience,
            options={"require": ["exp", "sub", "token_type", "aud"]},
        )
        if data["token_type"] != token_type or not isinstance(data["sub"], str):
            raise InvalidTokenError("Token 类型或用户标识无效")
        return UUID(data["sub"])
    except jwt.ExpiredSignatureError:
        raise BusinessException(ResultCodeEnum.UNAUTHORIZED, "登录态已过期") from None
    except InvalidTokenError, KeyError, TypeError, ValueError:
        raise BusinessException(ResultCodeEnum.UNAUTHORIZED, "登录态无效") from None


def create_access_token(user_id: UUID) -> str:
    settings = get_settings()
    return _create_token(
        user_id,
        secret=_require_secret(settings.auth_token_secret, "auth_token_secret"),
        expire_seconds=settings.auth_token_expire_seconds,
        token_type=_ACCESS_TOKEN_TYPE,
        audience=_ACCESS_TOKEN_AUDIENCE,
    )


def parse_access_token(token: str) -> UUID:
    settings = get_settings()
    return _parse_token(
        token,
        secret=_require_secret(settings.auth_token_secret, "auth_token_secret"),
        token_type=_ACCESS_TOKEN_TYPE,
        audience=_ACCESS_TOKEN_AUDIENCE,
    )


def create_admin_access_token(admin_id: UUID) -> str:
    settings = get_settings()
    return _create_token(
        admin_id,
        secret=_require_secret(settings.admin_token_secret, "admin_token_secret"),
        expire_seconds=settings.admin_token_expire_seconds,
        token_type=_ADMIN_TOKEN_TYPE,
        audience=_ADMIN_TOKEN_AUDIENCE,
    )


def parse_admin_access_token(token: str) -> UUID:
    settings = get_settings()
    return _parse_token(
        token,
        secret=_require_secret(settings.admin_token_secret, "admin_token_secret"),
        token_type=_ADMIN_TOKEN_TYPE,
        audience=_ADMIN_TOKEN_AUDIENCE,
    )

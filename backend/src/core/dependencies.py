from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.exceptions import BusinessException
from src.common.result_code import ResultCodeEnum
from src.core.auth_token import parse_access_token
from src.core.database import get_async_session

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]

_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
) -> UUID:
    """从 Bearer Token 中解析当前用户 ID。"""

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise BusinessException(ResultCodeEnum.UNAUTHORIZED)

    return parse_access_token(credentials.credentials)


CurrentUserIdDep = Annotated[UUID, Depends(get_current_user_id)]

from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.users.model import User
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


async def get_current_user(
    user_id: CurrentUserIdDep,
    session: SessionDep,
) -> User:
    """查询当前登录且未软删除的用户。"""

    user = await session.scalar(select(User).where(User.id == str(user_id)))
    if user is None:
        # 令牌对应用户已不存在时，按登录状态失效处理。
        raise BusinessException(ResultCodeEnum.UNAUTHORIZED)
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]

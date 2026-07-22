from functools import lru_cache
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.common.exceptions import BusinessException
from src.common.result_code import ResultCodeEnum
from src.core.config import settings


@lru_cache
def get_async_engine() -> AsyncEngine:
    if not settings.database_url:
        raise BusinessException(ResultCodeEnum.SYSTEM_ERROR, "database_url 未配置")

    return create_async_engine(
        settings.database_url, pool_pre_ping=True, echo=settings.database_echo
    )


@lru_cache
def get_async_session_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=get_async_engine(), expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_async_session_factory().begin() as session:
        yield session

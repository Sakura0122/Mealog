from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.meal_records.model import MealRecord
from src.api.users.model import User
from src.api.users.schema import (
    UserProfileResponse,
    UserProfileUpdate,
    UserStatisticsResponse,
)
from src.rustfs.url import build_public_file_url


def get_user_profile(user: User) -> UserProfileResponse:
    """查询当前用户资料。"""

    return _to_profile_response(user)


async def update_user_profile(
    payload: UserProfileUpdate,
    user: User,
    session: AsyncSession,
) -> UserProfileResponse:
    """仅更新当前用户的昵称和头像。"""

    user.nickname = payload.nickname
    user.avatar_object_key = payload.avatar_object_key
    await session.flush()
    return _to_profile_response(user)


async def get_user_statistics(user: User, session: AsyncSession) -> UserStatisticsResponse:
    """统计当前用户累计记录数和按进食日期去重后的记录天数。"""

    statement = select(
        func.count(MealRecord.id),
        func.count(func.distinct(func.date(MealRecord.eaten_at))),
    ).where(MealRecord.user_id == user.id)
    total_records, recorded_days = (await session.execute(statement)).one()
    return UserStatisticsResponse(
        total_records=total_records,
        recorded_days=recorded_days,
    )


def _to_profile_response(user: User) -> UserProfileResponse:
    """补充头像公开地址并转换为资料响应。"""

    avatar_url = (
        build_public_file_url(user.avatar_object_key)
        if user.avatar_object_key is not None
        else None
    )
    return UserProfileResponse(
        id=user.id,
        nickname=user.nickname,
        avatar_object_key=user.avatar_object_key,
        avatar_url=avatar_url,
    )

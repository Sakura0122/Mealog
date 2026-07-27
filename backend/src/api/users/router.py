from fastapi import APIRouter

from src.api.users import service as user_service
from src.api.users.schema import UserProfileResponse, UserProfileUpdate, UserStatisticsResponse
from src.common.result import Result
from src.core.dependencies import CurrentUserDep, SessionDep

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("/me", response_model=Result[UserProfileResponse], summary="查询当前用户资料")
async def get_current_user_profile(user: CurrentUserDep) -> Result[UserProfileResponse]:
    profile = user_service.get_user_profile(user)
    return Result.success(profile)


@router.put("/me", response_model=Result[UserProfileResponse], summary="更新当前用户资料")
async def update_current_user_profile(
    payload: UserProfileUpdate,
    user: CurrentUserDep,
    session: SessionDep,
) -> Result[UserProfileResponse]:
    profile = await user_service.update_user_profile(payload, user, session)
    return Result.success(profile)


@router.get(
    "/me/statistics",
    response_model=Result[UserStatisticsResponse],
    summary="查询当前用户饮食记录统计",
)
async def get_current_user_statistics(
    user: CurrentUserDep,
    session: SessionDep,
) -> Result[UserStatisticsResponse]:
    statistics = await user_service.get_user_statistics(user, session)
    return Result.success(statistics)

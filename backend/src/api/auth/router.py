from typing import Annotated

from fastapi import APIRouter, Body

from src.api.auth.schema import WechatLoginResponse
from src.api.auth.service import login_with_wechat
from src.common.result import Result
from src.core.dependencies import SessionDep

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post(
    "/wechat-login",
    response_model=Result[WechatLoginResponse],
    summary="微信登录",
    description="使用微信小程序登录凭证换取当前应用的访问令牌和用户信息。",
)
async def wechat_login(
    code: Annotated[
        str,
        Body(min_length=1, embed=True, description="微信小程序登录凭证"),
    ],
    session: SessionDep,
) -> Result[WechatLoginResponse]:
    return Result.success(await login_with_wechat(code, session))

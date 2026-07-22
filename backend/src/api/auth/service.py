from uuid import UUID

import httpx
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.schema import UserProfile, WechatLoginResponse
from src.api.users.model import User
from src.common.exceptions import BusinessException
from src.common.result_code import ResultCodeEnum
from src.core.auth_token import create_access_token
from src.core.config import get_settings

_WECHAT_CODE_TO_SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session"


class WechatSession(BaseModel):
    openid: str = Field(min_length=1)
    unionid: str | None = None


async def login_with_wechat(code: str, session: AsyncSession) -> WechatLoginResponse:
    """
    使用微信小程序登录凭证登录。

    :param code: 微信小程序登录凭证
    :param session: 数据库会话
    :return: 当前应用的访问令牌和用户信息
    """

    # 1. 使用登录凭证换取微信会话信息
    wechat_session = await code_to_session(code)

    # 2. 根据 OpenID 查询当前应用用户
    result = await session.execute(select(User).where(User.wechat_openid == wechat_session.openid))
    user = result.scalar_one_or_none()

    if user is None:
        # 3. 用户不存在时创建用户
        user = User(
            wechat_openid=wechat_session.openid,
            wechat_unionid=wechat_session.unionid,
        )
        session.add(user)
    elif wechat_session.unionid and user.wechat_unionid != wechat_session.unionid:
        # 4. 用户存在时同步最新的 UnionID
        user.wechat_unionid = wechat_session.unionid

    # 5. 刷新数据库生成的用户字段，事务由会话依赖统一提交
    await session.flush()
    await session.refresh(user)

    # 6. 生成访问令牌并返回用户资料
    return WechatLoginResponse(
        token=create_access_token(UUID(user.id)),
        user=UserProfile.model_validate(user),
    )


async def code_to_session(code: str) -> WechatSession:
    """
    使用微信登录凭证换取 OpenID 和 UnionID。

    :param code: 微信小程序登录凭证
    :return: 微信会话信息
    """

    settings = get_settings()
    if not settings.wechat_app_id or not settings.wechat_app_secret:
        raise BusinessException(
            ResultCodeEnum.SYSTEM_ERROR,
            "wechat_app_id 或 wechat_app_secret 未配置",
        )

    # 请求微信服务端的 code2Session 接口
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                _WECHAT_CODE_TO_SESSION_URL,
                params={
                    "appid": settings.wechat_app_id,
                    "secret": settings.wechat_app_secret,
                    "js_code": code,
                    "grant_type": "authorization_code",
                },
            )
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPError, ValueError:
        raise BusinessException(ResultCodeEnum.SYSTEM_ERROR, "微信登录服务请求失败") from None

    if not isinstance(data, dict):
        raise BusinessException(ResultCodeEnum.SYSTEM_ERROR, "微信登录服务响应异常")

    if "errcode" in data:
        message = data.get("errmsg")
        raise BusinessException(
            ResultCodeEnum.SYSTEM_ERROR,
            message if isinstance(message, str) else "微信登录失败",
        )

    # 严格校验微信成功响应，避免缺少 OpenID 时继续创建用户
    try:
        return WechatSession.model_validate(data)
    except ValidationError:
        raise BusinessException(ResultCodeEnum.SYSTEM_ERROR, "微信登录服务响应异常") from None

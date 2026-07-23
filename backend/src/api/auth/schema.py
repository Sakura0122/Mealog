from pydantic import BaseModel, ConfigDict


class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nickname: str | None
    avatar_object_key: str | None


class WechatLoginResponse(BaseModel):
    token: str
    user: UserProfile

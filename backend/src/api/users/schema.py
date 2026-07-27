from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserProfileResponse(BaseModel):
    """当前用户资料响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(description="用户 ID")
    nickname: str | None = Field(description="用户昵称，未设置时为空")
    avatar_object_key: str | None = Field(description="头像对象存储键，未设置时为空")
    avatar_url: str | None = Field(description="头像公开访问地址，未设置时为空")


class UserProfileUpdate(BaseModel):
    """当前用户资料更新参数。"""

    model_config = ConfigDict(extra="forbid")

    nickname: str = Field(min_length=1, max_length=64, description="用户昵称")
    avatar_object_key: str | None = Field(
        default=None,
        min_length=1,
        max_length=512,
        description="头像对象存储键，未设置时为空",
    )

    @field_validator("nickname")
    @classmethod
    def validate_nickname(cls, value: str) -> str:
        """去除昵称首尾空白并校验有效内容。"""

        value = value.strip()
        if not value:
            raise ValueError("用户昵称不能为空")
        return value


class UserStatisticsResponse(BaseModel):
    """当前用户饮食记录统计响应。"""

    total_records: int = Field(description="累计饮食记录数")
    recorded_days: int = Field(description="存在饮食记录的日期数")

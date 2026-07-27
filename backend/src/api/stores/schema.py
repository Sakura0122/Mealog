from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StoreCreate(BaseModel):
    """保存地图店铺请求。"""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=128, description="店铺名称")
    address: str | None = Field(default=None, max_length=255, description="店铺地址")
    latitude: Decimal = Field(ge=-90, le=90, description="店铺纬度")
    longitude: Decimal = Field(
        ge=-180,
        le=180,
        description="店铺经度",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """去除店铺名称首尾空白并校验有效内容。"""

        value = value.strip()
        if not value:
            raise ValueError("店铺名称不能为空")
        return value

    @field_validator("address")
    @classmethod
    def normalize_address(cls, value: str | None) -> str | None:
        """将空白地址规范为空值。"""

        if value is None:
            return None
        value = value.strip()
        return value or None


class StoreResponse(BaseModel):
    """历史店铺响应。"""

    id: str = Field(description="店铺 ID")
    name: str = Field(description="店铺名称")
    address: str | None = Field(description="店铺地址，地图未返回时为空")
    latitude: Decimal | None = Field(description="店铺纬度，历史数据未保存时为空")
    longitude: Decimal | None = Field(description="店铺经度，历史数据未保存时为空")
    usage_count: int = Field(description="关联该店铺的有效饮食记录数量")
    updated_at: datetime = Field(description="店铺最后更新时间")

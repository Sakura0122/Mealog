from datetime import date as Date
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

# 饮食来源：自己做或外面买。
MealSourceType = Literal["SELF_MADE", "DINING_OUT"]


class MealRecordImageInput(BaseModel):
    """饮食记录图片写入参数。"""

    original_object_key: str = Field(
        min_length=1,
        max_length=512,
        description="原始图片在对象存储中的文件键",
    )
    processed_object_key: str | None = Field(
        default=None,
        min_length=1,
        max_length=512,
        description="图片处理结果在对象存储中的文件键，未处理时为空",
    )


class MealRecordPayload(BaseModel):
    """饮食记录新增和更新共用参数。"""

    dish_name: str = Field(min_length=1, max_length=100, description="本次记录的菜品名称")
    eaten_at: datetime = Field(description="进食时间，不包含时区偏移")
    source_type: MealSourceType | None = Field(
        default=None,
        description="饮食来源：SELF_MADE 自己做，DINING_OUT 外面买",
    )
    store_id: UUID | None = Field(
        default=None,
        description="关联店铺 ID，仅外面买时可填写",
    )
    recipe_id: UUID | None = Field(
        default=None,
        description="关联菜谱 ID，仅自己做时可填写",
    )
    note: str | None = Field(default=None, max_length=1000, description="本次饮食记录的个人备注")
    images: list[MealRecordImageInput] = Field(
        default_factory=list,
        max_length=9,
        description="记录图片，按数组顺序展示，首张图片作为封面",
    )

    @field_validator("dish_name")
    @classmethod
    def validate_dish_name(cls, value: str) -> str:
        """去除菜品名称首尾空白并校验有效内容。"""

        value = value.strip()
        if not value:
            raise ValueError("菜品名称不能为空")
        return value

    @field_validator("eaten_at")
    @classmethod
    def validate_eaten_at(cls, value: datetime) -> datetime:
        """校验进食时间符合项目无时区时间约定。"""

        # DATETIME 不保存偏移量，只接受可原样写入和返回的无时区时间。
        if value.tzinfo is not None and value.utcoffset() is not None:
            raise ValueError("进食时间不能包含时区")
        return value


class MealRecordCreate(MealRecordPayload):
    """新增饮食记录请求。"""

    pass


class MealRecordUpdate(MealRecordPayload):
    """更新饮食记录请求。"""

    pass


class MealRecordImageResponse(BaseModel):
    """饮食记录图片响应。"""

    id: str = Field(description="图片记录 ID")
    original_object_key: str = Field(description="原始图片在对象存储中的文件键")
    original_url: str = Field(description="原始图片公开访问地址")
    processed_object_key: str | None = Field(
        description="图片处理结果在对象存储中的文件键，未处理时为空"
    )
    processed_url: str | None = Field(description="图片处理结果公开访问地址，未处理时为空")
    sort_order: int = Field(description="图片展示顺序，从 0 开始")
    is_cover: bool = Field(description="是否为当前饮食记录的封面")


class MealRecordListItemResponse(BaseModel):
    """饮食记录分页列表项响应。"""

    id: str = Field(description="饮食记录 ID")
    dish_name: str = Field(description="菜品名称")
    eaten_at: datetime = Field(description="进食时间，不包含时区偏移")
    note: str | None = Field(description="个人备注，未填写时为空")
    cover_url: str | None = Field(description="记录封面公开访问地址，无图片时为空")


class MealRecordCalendarDayResponse(BaseModel):
    """饮食记录月历中单日摘要响应。"""

    date: Date = Field(description="有饮食记录的日期")
    record_count: int = Field(description="该日期的饮食记录数量")
    cover_url: str | None = Field(description="该日期最新一条带图记录的封面地址")


class MealRecordCalendarResponse(BaseModel):
    """饮食记录月历汇总响应。"""

    month: str = Field(description="查询月份，格式为 YYYY-MM")
    total: int = Field(description="该月份的饮食记录总数")
    recorded_days: int = Field(description="该月份有饮食记录的天数")
    days: list[MealRecordCalendarDayResponse] = Field(description="有记录日期的月历摘要")


class MealRecordResponse(BaseModel):
    """饮食记录完整详情响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(description="饮食记录 ID")
    dish_name: str = Field(description="菜品名称")
    eaten_at: datetime = Field(description="进食时间，不包含时区偏移")
    source_type: MealSourceType | None = Field(
        description="饮食来源：SELF_MADE 自己做，DINING_OUT 外面买，未选择时为空"
    )
    store_id: str | None = Field(description="关联店铺 ID，未关联时为空")
    recipe_id: str | None = Field(description="关联菜谱 ID，未关联时为空")
    note: str | None = Field(description="个人备注，未填写时为空")
    images: list[MealRecordImageResponse] = Field(description="按展示顺序排列的记录图片")
    created_at: datetime = Field(description="记录创建时间")
    updated_at: datetime = Field(description="记录最后更新时间")

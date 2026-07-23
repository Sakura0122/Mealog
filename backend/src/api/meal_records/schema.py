from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

MealSourceType = Literal["SELF_MADE", "DINING_OUT"]


class MealRecordImageInput(BaseModel):
    original_object_key: str = Field(min_length=1, max_length=512)
    processed_object_key: str | None = Field(default=None, min_length=1, max_length=512)


class MealRecordPayload(BaseModel):
    dish_name: str = Field(min_length=1, max_length=100)
    eaten_at: datetime
    source_type: MealSourceType | None = None
    store_id: UUID | None = None
    recipe_id: UUID | None = None
    note: str | None = Field(default=None, max_length=1000)
    images: list[MealRecordImageInput] = Field(default_factory=list, max_length=9)

    @field_validator("dish_name")
    @classmethod
    def validate_dish_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("菜品名称不能为空")
        return value

    @field_validator("eaten_at")
    @classmethod
    def validate_eaten_at(cls, value: datetime) -> datetime:
        # DATETIME 不保存偏移量，只接受可原样写入和返回的无时区时间。
        if value.tzinfo is not None and value.utcoffset() is not None:
            raise ValueError("进食时间不能包含时区")
        return value


class MealRecordCreate(MealRecordPayload):
    pass


class MealRecordUpdate(MealRecordPayload):
    pass


class MealRecordImageResponse(BaseModel):
    id: str
    original_object_key: str
    original_url: str
    processed_object_key: str | None
    processed_url: str | None
    sort_order: int
    is_cover: bool


class MealRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dish_name: str
    eaten_at: datetime
    source_type: MealSourceType | None
    store_id: str | None
    recipe_id: str | None
    note: str | None
    images: list[MealRecordImageResponse]
    created_at: datetime
    updated_at: datetime

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

RecipeStatus = Literal["DRAFT", "COMPLETED"]


class RecipePayload(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    cover_object_key: str | None = Field(default=None, min_length=1, max_length=512)
    ingredients: list[str] = Field(default_factory=list, max_length=100)
    steps: str | None = Field(default=None, max_length=65535)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("菜谱名称不能为空")
        return value

    @field_validator("cover_object_key", "steps")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("ingredients")
    @classmethod
    def validate_ingredients(cls, values: list[str]) -> list[str]:
        normalized = [value.strip() for value in values]
        if any(not value for value in normalized):
            raise ValueError("食材名称不能为空")
        if any(len(value) > 100 for value in normalized):
            raise ValueError("食材名称不能超过 100 个字符")
        return normalized


class RecipeCreate(RecipePayload):
    pass


class RecipeUpdate(RecipePayload):
    pass


class RecipeListItemResponse(BaseModel):
    id: str
    name: str
    cover_url: str | None
    status: RecipeStatus
    usage_count: int
    updated_at: datetime


class RecipeResponse(BaseModel):
    id: str
    name: str
    cover_object_key: str | None
    cover_url: str | None
    ingredients: list[str]
    steps: str | None
    status: RecipeStatus
    usage_count: int
    created_at: datetime
    updated_at: datetime

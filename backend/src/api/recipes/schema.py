from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

# 菜谱状态：草稿或已完善。
RecipeStatus = Literal["DRAFT", "COMPLETED"]


class RecipePayload(BaseModel):
    """菜谱新增和更新共用参数。"""

    name: str = Field(min_length=1, max_length=100, description="菜谱名称，同一用户下不可重复")
    cover_object_key: str | None = Field(
        default=None,
        min_length=1,
        max_length=512,
        description="菜谱封面在对象存储中的文件键，无封面时为空",
    )
    ingredients: list[str] = Field(
        default_factory=list,
        max_length=100,
        description="按展示顺序排列的食材名称，未填写时为空数组",
    )
    steps: str | None = Field(
        default=None,
        max_length=65535,
        description="菜谱制作步骤，未填写时为空",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """去除菜谱名称首尾空白并校验有效内容。"""

        value = value.strip()
        if not value:
            raise ValueError("菜谱名称不能为空")
        return value

    @field_validator("cover_object_key", "steps")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        """将可选文本规范为去除首尾空白后的值或空值。"""

        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("ingredients")
    @classmethod
    def validate_ingredients(cls, values: list[str]) -> list[str]:
        """规范食材名称并校验每项均有有效内容。"""

        normalized = [value.strip() for value in values]
        if any(not value for value in normalized):
            raise ValueError("食材名称不能为空")
        if any(len(value) > 100 for value in normalized):
            raise ValueError("食材名称不能超过 100 个字符")
        return normalized


class RecipeCreate(RecipePayload):
    """新增菜谱请求。"""

    pass


class RecipeUpdate(RecipePayload):
    """更新菜谱请求。"""

    pass


class RecipeListItemResponse(BaseModel):
    """菜谱分页列表项响应。"""

    id: str = Field(description="菜谱 ID")
    name: str = Field(description="菜谱名称")
    cover_url: str | None = Field(description="菜谱封面公开访问地址，无封面时为空")
    status: RecipeStatus = Field(description="菜谱状态：DRAFT 草稿，COMPLETED 已完善")
    usage_count: int = Field(description="关联该菜谱的有效饮食记录数量")
    updated_at: datetime = Field(description="菜谱最后更新时间")


class RecipeResponse(BaseModel):
    """菜谱完整详情响应。"""

    id: str = Field(description="菜谱 ID")
    name: str = Field(description="菜谱名称")
    cover_object_key: str | None = Field(description="菜谱封面在对象存储中的文件键，无封面时为空")
    cover_url: str | None = Field(description="菜谱封面公开访问地址，无封面时为空")
    ingredients: list[str] = Field(description="按展示顺序排列的食材名称")
    steps: str | None = Field(description="菜谱制作步骤，未填写时为空")
    status: RecipeStatus = Field(description="菜谱状态：DRAFT 草稿，COMPLETED 已完善")
    usage_count: int = Field(description="关联该菜谱的有效饮食记录数量")
    created_at: datetime = Field(description="菜谱创建时间")
    updated_at: datetime = Field(description="菜谱最后更新时间")


class RecipeShareResponse(BaseModel):
    """分享菜谱公开详情响应。"""

    id: str = Field(description="原菜谱 ID")
    name: str = Field(description="菜谱名称")
    cover_url: str | None = Field(description="菜谱封面公开访问地址，无封面时为空")
    ingredients: list[str] = Field(description="按展示顺序排列的食材名称")
    steps: str | None = Field(description="菜谱制作步骤，未填写时为空")


class RecipeSavedResponse(BaseModel):
    """保存分享菜谱响应。"""

    id: str = Field(description="保存后生成的菜谱 ID")

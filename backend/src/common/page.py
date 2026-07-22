from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from src.common.exceptions import BusinessException
from src.common.result_code import ResultCodeEnum

T = TypeVar("T")


class PageRequest(BaseModel):
    current_page: int = Field(default=1, ge=1, description="当前页数")
    page_size: int = Field(default=10, ge=1, description="每页显示条目个数")
    sort_field: str | None = Field(default=None, description="排序字段")
    is_asc: bool = Field(default=True, description="是否升序")

    @property
    def offset(self) -> int:
        return (self.current_page - 1) * self.page_size

    def to_order_by(
        self, allowed_sort_fields: dict[str, Any], default_orders: Sequence[Any]
    ) -> list[Any]:
        if not self.sort_field:
            return list(default_orders)

        sort_column = allowed_sort_fields.get(self.sort_field)
        if sort_column is None:
            raise BusinessException(ResultCodeEnum.PARAM_ERROR, "排序字段不支持")

        return [sort_column.asc() if self.is_asc else sort_column.desc()]


class PageResult(BaseModel, Generic[T]):
    model_config = ConfigDict(populate_by_name=True)

    total: int = Field(description="总条数")
    page_count: int = Field(description="总页数")
    items: list[T] = Field(alias="list", description="当前页数据")

    @classmethod
    def of(cls, page: PageRequest, total: int, items: list[T]) -> "PageResult[T]":
        page_count = (total + page.page_size - 1) // page.page_size
        return cls(total=total, page_count=page_count, list=items)

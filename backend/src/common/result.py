from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Result(BaseModel, Generic[T]):
    code: int
    message: str
    data: T | None

    @staticmethod
    def success(data: T | None = None) -> "Result[T]":
        return Result(code=200, message="成功", data=data)

    @staticmethod
    def error(code: int, message: str) -> "Result[None]":
        return Result(code=code, message=message, data=None)

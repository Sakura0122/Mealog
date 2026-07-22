from enum import Enum


class ResultCodeEnum(Enum):
    PARAM_ERROR = (400, "请求参数错误")
    UNAUTHORIZED = (401, "请先登录")
    NO_AUTH_ERROR = (403, "无权限")
    NOT_FOUND_ERROR = (404, "请求数据不存在")
    SYSTEM_ERROR = (500, "服务器内部错误")

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message

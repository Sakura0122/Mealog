from src.common.result_code import ResultCodeEnum


class BusinessException(Exception):
    def __init__(self, code: int | ResultCodeEnum, message: str | None = None):
        if isinstance(code, ResultCodeEnum):
            self.code = code.code
            self.message = message or code.message
        else:
            self.code = code
            self.message = message or "请求处理失败"

        super().__init__(self.message)

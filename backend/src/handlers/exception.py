from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.exceptions import HTTPException

from src.common.exceptions import BusinessException
from src.common.result import Result
from src.common.result_code import ResultCodeEnum


def _get_validation_message(error: dict | None) -> str:
    if not error:
        return "请求参数错误"

    error_type = error.get("type")
    ctx = error.get("ctx") or {}

    if error_type == "missing":
        return "缺少必填参数"

    if error_type == "string_too_short":
        min_length = ctx.get("min_length")
        if min_length == 1:
            return "参数不能为空"
        return f"参数不能少于 {min_length} 个字符"

    if error_type == "string_too_long":
        return f"参数不能超过 {ctx.get('max_length')} 个字符"

    if error_type == "json_invalid":
        return "请求体不是合法 JSON"

    if error_type in {"uuid_parsing", "uuid_type"}:
        return "参数格式不正确"

    if error_type in {"string_type", "int_type", "bool_type", "list_type", "dict_type"}:
        return "参数类型不正确"

    return "请求参数错误"


def validation_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    error = exc.errors()[0] if exc.errors() else None
    message = _get_validation_message(error)
    return JSONResponse(
        content=Result.error(code=ResultCodeEnum.PARAM_ERROR.code, message=message).model_dump()
    )


def business_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, BusinessException)

    if exc.code >= ResultCodeEnum.SYSTEM_ERROR.code:
        logger.opt(exception=exc).error(
            "业务处理发生系统错误，method={}，path={}，code={}，message={}",
            request.method,
            request.url.path,
            exc.code,
            exc.message,
        )
    elif exc.code in {
        ResultCodeEnum.UNAUTHORIZED.code,
        ResultCodeEnum.NO_AUTH_ERROR.code,
    }:
        logger.warning(
            "请求鉴权失败，method={}，path={}，code={}，message={}",
            request.method,
            request.url.path,
            exc.code,
            exc.message,
        )

    return JSONResponse(content=Result.error(code=exc.code, message=exc.message).model_dump())


def http_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, HTTPException)
    message = exc.detail if isinstance(exc.detail, str) else "请求处理失败"
    return JSONResponse(content=Result.error(code=exc.status_code, message=message).model_dump())


def exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.opt(exception=exc).error("未处理的服务器异常")
    return JSONResponse(
        content=Result.error(
            code=ResultCodeEnum.SYSTEM_ERROR.code,
            message=ResultCodeEnum.SYSTEM_ERROR.message,
        ).model_dump()
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(BusinessException, business_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, exception_handler)

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from serving_engine.errors.codes import INTERNAL_ERROR, INVALID_ARGUMENT, NO_DATA
from serving_engine.schemas.common import ErrorDetail, ErrorResponse


def build_error_response(status_code: int, code: str, message: str) -> JSONResponse:
    """
    以統一 schema 組裝 JSON error response。
    """
    payload = ErrorResponse(error=ErrorDetail(code=code, message=message))
    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(),
    )


def _format_request_validation_error(exc: RequestValidationError) -> str:
    """
    將 FastAPI request validation error 壓成簡潔的一行訊息。
    """
    errors = exc.errors()
    if not errors:
        return "Request validation failed"

    first = errors[0]
    location = ".".join(str(part) for part in first.get("loc", ()))
    message = str(first.get("msg", "Invalid request"))
    if location:
        return f"{location}: {message}"
    return message


async def _handle_value_error(request: Request, exc: ValueError) -> JSONResponse:
    """
    將 ValueError 映射為 400 INVALID_ARGUMENT。
    """
    _ = request
    return build_error_response(
        status_code=400,
        code=INVALID_ARGUMENT,
        message=str(exc),
    )


async def _handle_file_not_found_error(
    request: Request,
    exc: FileNotFoundError,
) -> JSONResponse:
    """
    將 FileNotFoundError 映射為 404 NO_DATA。
    """
    _ = request
    return build_error_response(
        status_code=404,
        code=NO_DATA,
        message=str(exc),
    )


async def _handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    """
    將未預期錯誤映射為 500 INTERNAL_ERROR。
    """
    _ = (request, exc)
    return build_error_response(
        status_code=500,
        code=INTERNAL_ERROR,
        message="Internal server error",
    )


async def _handle_request_validation_error(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """
    將 FastAPI request validation error 映射為 400 INVALID_ARGUMENT。
    """
    _ = request
    return build_error_response(
        status_code=400,
        code=INVALID_ARGUMENT,
        message=_format_request_validation_error(exc),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    註冊 serving engine 第一版的統一 exception handlers。
    """
    app.add_exception_handler(RequestValidationError, _handle_request_validation_error)
    app.add_exception_handler(ValueError, _handle_value_error)
    app.add_exception_handler(FileNotFoundError, _handle_file_not_found_error)
    app.add_exception_handler(Exception, _handle_unexpected_error)

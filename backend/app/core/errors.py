import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("signaltally")


class AppError(Exception):
    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class InvalidApiKeyError(AppError):
    def __init__(self, message: str = "The provided API key is invalid or inactive."):
        super().__init__("invalid_api_key", message, status.HTTP_401_UNAUTHORIZED)


class MissingApiKeyError(AppError):
    def __init__(self, message: str = "X-Client-Id and X-Api-Key headers are required."):
        super().__init__("missing_api_key", message, status.HTTP_401_UNAUTHORIZED)


class ServiceNotEnabledError(AppError):
    def __init__(self, message: str = "This API key is not authorized for this service."):
        super().__init__("service_not_enabled", message, status.HTTP_403_FORBIDDEN)


class PayloadTooLargeError(AppError):
    def __init__(self, message: str = "This request exceeds the maximum allowed size."):
        super().__init__("payload_too_large", message, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)


def _error_body(error_code: str, message: str, request: Request) -> dict:
    return {
        "error": error_code,
        "message": message,
        "request_id": getattr(request.state, "request_id", None),
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.error_code, exc.message, request),
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(request: Request, exc: StarletteHTTPException):
        code_map = {401: "unauthorized", 403: "forbidden", 404: "not_found", 405: "method_not_allowed"}
        error_code = code_map.get(exc.status_code, "http_error")
        message = exc.detail if isinstance(exc.detail, str) else "Request failed."
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(error_code, message, request),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        first = exc.errors()[0] if exc.errors() else {}
        field = ".".join(str(loc) for loc in first.get("loc", []) if loc != "body")
        detail = first.get("msg", "Invalid request payload.")
        message = f"{field}: {detail}" if field else detail
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_body("invalid_payload", message, request),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception):
        logger.exception("Unhandled error", extra={"request_id": getattr(request.state, "request_id", None)})
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_body("internal_error", "Something went wrong on our end.", request),
        )
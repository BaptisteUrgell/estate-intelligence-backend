from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions.base import DomainException


async def global_domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    # Here we can add mapping for specific error codes if needed
    # For now, default to 400 Bad Request
    http_status = status.HTTP_400_BAD_REQUEST

    # We could implement a registry of HTTP status codes per error code

    return JSONResponse(
        status_code=http_status,
        content={
            "type": "about:blank",
            "title": "Business Rule Violation",
            "status": http_status,
            "detail": exc.message,
            "error_code": exc.error_code,
        },
        headers={"Content-Type": "application/problem+json"},
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    invalid_params = [
        {"loc": " -> ".join(map(str, err["loc"])), "msg": err["msg"], "type": err["type"]}
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "type": "about:blank",
            "title": "Validation Error",
            "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "detail": "Your request parameters didn't validate.",
            "invalid_params": invalid_params,
        },
        headers={"Content-Type": "application/problem+json"},
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": "about:blank",
            "title": "HTTP Error",
            "status": exc.status_code,
            "detail": str(exc.detail),
        },
        headers={"Content-Type": "application/problem+json"},
    )

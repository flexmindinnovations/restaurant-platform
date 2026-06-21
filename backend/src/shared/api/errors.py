from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse

from shared.domain.exceptions import (
    AuthenticationException,
    AuthorizationException,
    BusinessRuleViolationError,
    ConcurrencyError,
    DomainException,
    NotFoundException,
    ValidationException,
)


def domain_exception_handler(_request: Request, exc: DomainException) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=400,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


def not_found_handler(_request: Request, exc: NotFoundException) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=404,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


def authorization_handler(_request: Request, exc: AuthorizationException) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=403,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


def authentication_handler(_request: Request, exc: AuthenticationException) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=401,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


def validation_handler(_request: Request, exc: ValidationException) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=422,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


def business_rule_handler(_request: Request, exc: BusinessRuleViolationError) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=422,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


def concurrency_handler(_request: Request, exc: ConcurrencyError) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=409,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


def register_error_handlers(app: FastAPI) -> None:
    """Register all custom domain exception handlers on the FastAPI application."""
    app.add_exception_handler(DomainException, domain_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(NotFoundException, not_found_handler)  # type: ignore[arg-type]
    app.add_exception_handler(AuthorizationException, authorization_handler)  # type: ignore[arg-type]
    app.add_exception_handler(AuthenticationException, authentication_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ValidationException, validation_handler)  # type: ignore[arg-type]
    app.add_exception_handler(BusinessRuleViolationError, business_rule_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ConcurrencyError, concurrency_handler)  # type: ignore[arg-type]

from fastapi import Request
from fastapi.responses import ORJSONResponse

from shared.domain.exceptions import (
    AuthorizationError,
    BusinessRuleViolationError,
    ConcurrencyError,
    DomainException,
    EntityNotFoundError,
)


async def domain_exception_handler(request: Request, exc: DomainException) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=400,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


async def not_found_handler(request: Request, exc: EntityNotFoundError) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=404,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


async def authorization_handler(request: Request, exc: AuthorizationError) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=403,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


async def business_rule_handler(request: Request, exc: BusinessRuleViolationError) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=422,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


async def concurrency_handler(request: Request, exc: ConcurrencyError) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=409,
        content={"error": {"code": exc.code, "message": exc.message}},
    )

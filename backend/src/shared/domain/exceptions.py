class DomainException(Exception):
    def __init__(self, message: str, code: str = "DOMAIN_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundException(DomainException):
    def __init__(self, message: str, code: str = "NOT_FOUND") -> None:
        super().__init__(message=message, code=code)


class EntityNotFoundError(NotFoundException):
    def __init__(self, entity_type: str, entity_id: str) -> None:
        super().__init__(
            message=f"{entity_type} with id '{entity_id}' not found",
            code="NOT_FOUND",
        )


class BusinessRuleViolationError(DomainException):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, code="BUSINESS_RULE_VIOLATION")


class AuthorizationException(DomainException):
    def __init__(self, message: str = "Not authorized", code: str = "AUTHORIZATION_ERROR") -> None:
        super().__init__(message=message, code=code)


class AuthorizationError(AuthorizationException):
    def __init__(self, message: str = "Not authorized") -> None:
        super().__init__(message=message, code="AUTHORIZATION_ERROR")


class ConcurrencyError(DomainException):
    def __init__(self, entity_type: str) -> None:
        super().__init__(
            message=f"Concurrent modification detected on {entity_type}",
            code="CONCURRENCY_ERROR",
        )


class ValidationException(DomainException):
    def __init__(self, message: str, code: str = "VALIDATION_ERROR") -> None:
        super().__init__(message=message, code=code)

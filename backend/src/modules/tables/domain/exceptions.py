from shared.domain.exceptions import BusinessRuleViolationError, DomainException, EntityNotFoundError


class TableNotFoundError(EntityNotFoundError):
    def __init__(self, table_id: str) -> None:
        super().__init__(entity_type="Table", entity_id=table_id)


class SectionNotFoundError(EntityNotFoundError):
    def __init__(self, section_id: str) -> None:
        super().__init__(entity_type="Section", entity_id=section_id)


class ReservationNotFoundError(EntityNotFoundError):
    def __init__(self, reservation_id: str) -> None:
        super().__init__(entity_type="Reservation", entity_id=reservation_id)


class WaitlistEntryNotFoundError(EntityNotFoundError):
    def __init__(self, entry_id: str) -> None:
        super().__init__(entity_type="WaitlistEntry", entity_id=entry_id)


class TableNotAvailableError(BusinessRuleViolationError):
    def __init__(self, table_id: str) -> None:
        super().__init__(message=f"Table '{table_id}' is not available for seating")


class TableCapacityExceededError(BusinessRuleViolationError):
    def __init__(self, table_id: str, party_size: int) -> None:
        super().__init__(message=f"Table '{table_id}' cannot accommodate a party of {party_size}")


class DuplicateTableNumberError(DomainException):
    def __init__(self, restaurant_id: str, table_number: str) -> None:
        super().__init__(
            message=f"Table number '{table_number}' already exists for restaurant '{restaurant_id}'",
            code="DUPLICATE_TABLE_NUMBER",
        )


class ReservationConflictError(BusinessRuleViolationError):
    def __init__(self, table_id: str, date: str, time: str) -> None:
        super().__init__(message=f"Table '{table_id}' already has a reservation on {date} at {time}")

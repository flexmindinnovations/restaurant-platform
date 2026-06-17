from dataclasses import dataclass, field

from shared.domain.events import DomainEvent


@dataclass(frozen=True)
class AccountCreated(DomainEvent):
    email: str = ""
    roles: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AccountVerified(DomainEvent):
    pass


@dataclass(frozen=True)
class AccountDeactivated(DomainEvent):
    pass


@dataclass(frozen=True)
class PasswordChanged(DomainEvent):
    pass


@dataclass(frozen=True)
class RoleAssigned(DomainEvent):
    role: str = ""

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from modules.identity.domain.events.account_events import (
    AccountCreated,
    AccountDeactivated,
    AccountVerified,
    PasswordChanged,
    RoleAssigned,
)
from modules.identity.domain.value_objects.email import Email
from modules.identity.domain.value_objects.password import Password
from modules.identity.domain.value_objects.phone_number import PhoneNumber
from modules.identity.domain.value_objects.role import Role
from shared.domain.entity import AggregateRoot
from shared.domain.exceptions import ValidationException


@dataclass
class Account(AggregateRoot):
    email: Email = None  # type: ignore[assignment]
    password_hash: str = ""
    phone_number: PhoneNumber | None = None
    is_verified: bool = False
    is_active: bool = True
    verification_token: str | None = None
    reset_token: str | None = None
    reset_token_expires_at: datetime | None = None
    roles: list[Role] = field(default_factory=list)

    @classmethod
    def register(
        cls,
        email: Email,
        password: Password,
        phone_number: PhoneNumber | None = None,
        verification_token: str | None = None,
        roles: list[Role] | None = None,
    ) -> "Account":
        account_id = uuid.uuid4()
        if roles is None:
            roles = [Role.CUSTOMER]

        account = cls(
            id=account_id,
            email=email,
            password_hash=password.hashed_value,
            phone_number=phone_number,
            is_verified=False,
            is_active=True,
            verification_token=verification_token,
            roles=roles,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        account.register_event(
            AccountCreated(
                aggregate_id=account_id,
                email=email.value,
                roles=[r.value for r in roles],
            )
        )
        return account

    def verify_email(self, token: str) -> None:
        if not self.is_active:
            raise ValidationException("Account is inactive")
        if self.is_verified:
            return  # Already verified, idempotent
        if not self.verification_token or self.verification_token != token:
            raise ValidationException("Invalid verification token")

        self.is_verified = True
        self.verification_token = None
        self.updated_at = datetime.now(UTC)
        self.register_event(AccountVerified(aggregate_id=self.id))

    def deactivate(self) -> None:
        if not self.is_active:
            return
        self.is_active = False
        self.updated_at = datetime.now(UTC)
        self.register_event(AccountDeactivated(aggregate_id=self.id))

    def add_role(self, role: Role) -> None:
        if role not in self.roles:
            self.roles.append(role)
            self.updated_at = datetime.now(UTC)
            self.register_event(RoleAssigned(aggregate_id=self.id, role=role.value))

    def remove_role(self, role: Role) -> None:
        if role in self.roles:
            if len(self.roles) <= 1:
                raise ValidationException("An account must have at least one role")
            self.roles.remove(role)
            self.updated_at = datetime.now(UTC)

    def change_password(self, new_password: Password) -> None:
        if not self.is_active:
            raise ValidationException("Account is inactive")
        self.password_hash = new_password.hashed_value
        self.updated_at = datetime.now(UTC)
        self.register_event(PasswordChanged(aggregate_id=self.id))

    def request_password_reset(self, token: str, expires_at: datetime) -> None:
        if not self.is_active:
            raise ValidationException("Account is inactive")
        self.reset_token = token
        self.reset_token_expires_at = expires_at
        self.updated_at = datetime.now(UTC)

    def reset_password(self, token: str, new_password: Password) -> None:
        if not self.is_active:
            raise ValidationException("Account is inactive")
        if not self.reset_token or self.reset_token != token:
            raise ValidationException("Invalid reset token")
        if not self.reset_token_expires_at or datetime.now(UTC) > self.reset_token_expires_at:
            raise ValidationException("Reset token has expired")
        self.password_hash = new_password.hashed_value
        self.reset_token = None
        self.reset_token_expires_at = None
        self.updated_at = datetime.now(UTC)
        self.register_event(PasswordChanged(aggregate_id=self.id))

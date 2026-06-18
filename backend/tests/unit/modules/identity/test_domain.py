import pytest

from modules.identity.domain.entities.account import Account
from modules.identity.domain.value_objects.email import Email
from modules.identity.domain.value_objects.password import Password
from modules.identity.domain.value_objects.phone_number import PhoneNumber
from modules.identity.domain.value_objects.role import Role
from shared.domain.exceptions import ValidationException


@pytest.mark.unit
def test_email_valid():
    email = Email("  TEST@example.com  ")
    assert email.value == "test@example.com"


@pytest.mark.unit
def test_email_invalid():
    invalid_emails = ["invalid-email", "@domain.com", "user@domain", "", "   "]
    for val in invalid_emails:
        with pytest.raises(ValidationException):
            Email(val)


@pytest.mark.unit
def test_password_valid():
    # Helper dummy hash function
    dummy_hash = lambda x: f"hashed_{x}"
    pwd = Password.create("SecurePass123!", dummy_hash)
    assert pwd.hashed_value == "hashed_SecurePass123!"


@pytest.mark.unit
def test_password_invalid():
    dummy_hash = lambda x: f"hashed_{x}"
    invalid_passwords = [
        "short",  # < 8 chars
        "nouppercase1!",  # missing uppercase
        "NOLOWERCASE1!",  # missing lowercase
        "NoSpecialChar1",  # missing special
        "NoNumbers!_abc",  # missing digits
    ]
    for val in invalid_passwords:
        with pytest.raises(ValidationException):
            Password.create(val, dummy_hash)


@pytest.mark.unit
def test_phone_number_valid():
    phone = PhoneNumber("  +1-234-567-8901 ")
    assert phone.value == "+12345678901"


@pytest.mark.unit
def test_phone_number_invalid():
    invalid_phones = ["1234567890", "+12", "+", "", "   ", "+12345abc"]
    for val in invalid_phones:
        with pytest.raises(ValidationException):
            PhoneNumber(val)


@pytest.mark.unit
def test_account_registration():
    email = Email("customer@example.com")
    password = Password.from_hash("hashed_password")
    phone = PhoneNumber("+1234567890")

    account = Account.register(
        email=email, password=password, phone_number=phone, verification_token="token123", roles=[Role.CUSTOMER]
    )

    assert account.email == email
    assert account.password_hash == "hashed_password"
    assert account.phone_number == phone
    assert account.is_verified is False
    assert account.is_active is True
    assert account.verification_token == "token123"
    assert account.roles == [Role.CUSTOMER]

    events = account.collect_events()
    assert len(events) == 1
    assert events[0].email == "customer@example.com"
    assert events[0].roles == ["CUSTOMER"]


@pytest.mark.unit
def test_account_email_verification():
    account = Account.register(
        email=Email("test@example.com"), password=Password.from_hash("hashed_pwd"), verification_token="my_token"
    )
    account.collect_events()  # Clear registration event

    # Verify with wrong token
    with pytest.raises(ValidationException):
        account.verify_email("wrong_token")

    assert account.is_verified is False

    # Verify with correct token
    account.verify_email("my_token")
    assert account.is_verified is True
    assert account.verification_token is None

    events = account.collect_events()
    # collect_events in register has been cleared, so we only see AccountVerified
    assert len(events) == 1


@pytest.mark.unit
def test_account_deactivation():
    account = Account.register(email=Email("test@example.com"), password=Password.from_hash("hashed_pwd"))
    assert account.is_active is True

    account.deactivate()
    assert account.is_active is False

    # Verification and change password should fail on deactivated accounts
    with pytest.raises(ValidationException):
        account.verify_email("any")

    with pytest.raises(ValidationException):
        account.change_password(Password.from_hash("new"))


@pytest.mark.unit
def test_account_change_password():
    account = Account.register(email=Email("test@example.com"), password=Password.from_hash("old_hash"))

    account.change_password(Password.from_hash("new_hash"))
    assert account.password_hash == "new_hash"


@pytest.mark.unit
def test_account_roles():
    account = Account.register(email=Email("test@example.com"), password=Password.from_hash("hash"))
    assert account.roles == [Role.CUSTOMER]

    account.add_role(Role.RESTAURANT_OWNER)
    assert Role.RESTAURANT_OWNER in account.roles

    account.remove_role(Role.CUSTOMER)
    assert account.roles == [Role.RESTAURANT_OWNER]

    # Cannot remove last role
    with pytest.raises(ValidationException):
        account.remove_role(Role.RESTAURANT_OWNER)

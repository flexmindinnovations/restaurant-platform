import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from modules.notifications.application.commands.send_notification import (
    SendNotificationCommand,
    SendNotificationHandler,
)
from modules.notifications.domain.entities.notification import (
    Notification,
    NotificationChannel,
    NotificationStatus,
)

# --- Domain tests ---


@pytest.mark.unit
def test_notification_create():
    recipient = uuid.uuid4()
    n = Notification.create(
        recipient_id=recipient,
        channel=NotificationChannel.EMAIL,
        title="Order Placed",
        body="Your order #1234 has been placed.",
    )

    assert n.recipient_id == recipient
    assert n.channel == NotificationChannel.EMAIL
    assert n.title == "Order Placed"
    assert n.body == "Your order #1234 has been placed."
    assert n.status == NotificationStatus.PENDING
    assert n.sent_at is None
    assert n.error_message is None
    assert n.id is not None
    assert n.created_at is not None


@pytest.mark.unit
def test_notification_mark_sent():
    n = Notification.create(
        recipient_id=uuid.uuid4(),
        channel=NotificationChannel.EMAIL,
        title="Test",
        body="Body",
    )

    n.mark_sent()
    assert n.status == NotificationStatus.SENT
    assert n.sent_at is not None


@pytest.mark.unit
def test_notification_mark_failed():
    n = Notification.create(
        recipient_id=uuid.uuid4(),
        channel=NotificationChannel.SMS,
        title="Test",
        body="Body",
    )

    n.mark_failed("SMTP connection refused")
    assert n.status == NotificationStatus.FAILED
    assert n.error_message == "SMTP connection refused"


@pytest.mark.unit
def test_notification_channels():
    assert NotificationChannel.EMAIL == "EMAIL"
    assert NotificationChannel.SMS == "SMS"
    assert NotificationChannel.PUSH == "PUSH"


@pytest.mark.unit
def test_notification_statuses():
    assert NotificationStatus.PENDING == "PENDING"
    assert NotificationStatus.SENT == "SENT"
    assert NotificationStatus.FAILED == "FAILED"


# --- Command handler tests ---


class MockUow:
    def __init__(self):
        self.committed = False
        self.aggregates = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def register_aggregate(self, aggregate):
        self.aggregates.append(aggregate)

    async def commit(self):
        self.committed = True


@pytest.fixture
def mock_notification_repo():
    repo = MagicMock()
    repo.add = AsyncMock()
    repo.update = AsyncMock()
    repo.get_by_id = AsyncMock()
    return repo


@pytest.fixture
def mock_dispatcher():
    dispatcher = MagicMock()
    dispatcher.dispatch = AsyncMock()
    return dispatcher


@pytest.mark.unit
@pytest.mark.asyncio
async def test_send_notification_success(mock_notification_repo, mock_dispatcher):
    uow = MockUow()
    handler = SendNotificationHandler(mock_notification_repo, mock_dispatcher, uow)

    command = SendNotificationCommand(
        recipient_id=uuid.uuid4(),
        channel=NotificationChannel.EMAIL,
        title="Order Confirmed",
        body="Your order has been confirmed.",
    )

    notification_id = await handler.handle(command)

    assert notification_id is not None
    mock_notification_repo.add.assert_called_once()
    mock_dispatcher.dispatch.assert_called_once()
    # update called once for the _save after dispatch
    mock_notification_repo.update.assert_called_once()

    saved_notification = mock_notification_repo.update.call_args[0][0]
    assert saved_notification.status == NotificationStatus.SENT
    assert saved_notification.sent_at is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_send_notification_dispatch_failure(mock_notification_repo, mock_dispatcher):
    mock_dispatcher.dispatch = AsyncMock(side_effect=Exception("SMTP timeout"))
    uow = MockUow()
    handler = SendNotificationHandler(mock_notification_repo, mock_dispatcher, uow)

    command = SendNotificationCommand(
        recipient_id=uuid.uuid4(),
        channel=NotificationChannel.EMAIL,
        title="Order Placed",
        body="Your order has been placed.",
    )

    notification_id = await handler.handle(command)

    assert notification_id is not None
    mock_notification_repo.update.assert_called_once()

    saved_notification = mock_notification_repo.update.call_args[0][0]
    assert saved_notification.status == NotificationStatus.FAILED
    assert saved_notification.error_message == "SMTP timeout"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_send_notification_sms_channel(mock_notification_repo, mock_dispatcher):
    uow = MockUow()
    handler = SendNotificationHandler(mock_notification_repo, mock_dispatcher, uow)

    command = SendNotificationCommand(
        recipient_id=uuid.uuid4(),
        channel=NotificationChannel.SMS,
        title="Delivery Update",
        body="Your delivery is on the way!",
    )

    notification_id = await handler.handle(command)
    assert notification_id is not None

    added_notification = mock_notification_repo.add.call_args[0][0]
    assert added_notification.channel == NotificationChannel.SMS


@pytest.mark.unit
@pytest.mark.asyncio
async def test_send_notification_push_channel(mock_notification_repo, mock_dispatcher):
    uow = MockUow()
    handler = SendNotificationHandler(mock_notification_repo, mock_dispatcher, uow)

    command = SendNotificationCommand(
        recipient_id=uuid.uuid4(),
        channel=NotificationChannel.PUSH,
        title="New Order",
        body="You have a new order!",
    )

    notification_id = await handler.handle(command)
    assert notification_id is not None

    added_notification = mock_notification_repo.add.call_args[0][0]
    assert added_notification.channel == NotificationChannel.PUSH

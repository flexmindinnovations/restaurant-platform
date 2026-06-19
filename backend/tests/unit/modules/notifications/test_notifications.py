import uuid
from unittest.mock import AsyncMock, MagicMock, patch

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
from modules.notifications.event_handlers import (
    handle_delivery_completed,
    handle_order_confirmed,
    handle_order_placed,
    handle_partner_assigned,
)
from workers.tasks.notification_tasks import send_notification_async

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


@pytest.fixture(autouse=True)
def mock_celery_task():
    with patch("workers.tasks.notification_tasks.send_notification_task.delay") as mock:
        yield mock


@pytest.mark.unit
@pytest.mark.asyncio
async def test_send_notification_success(mock_notification_repo, mock_dispatcher, mock_celery_task):
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
    mock_celery_task.assert_called_once_with(str(notification_id))

    added_notification = mock_notification_repo.add.call_args[0][0]
    assert added_notification.status == NotificationStatus.PENDING


# --- Celery Task Tests ---


@pytest.mark.unit
@pytest.mark.asyncio
@patch("workers.tasks.notification_tasks.get_session_factory")
@patch("workers.tasks.notification_tasks.SqlAlchemyNotificationRepository")
@patch("workers.tasks.notification_tasks.CompositeNotificationDispatcher")
async def test_send_notification_task_success(mock_dispatcher_class, mock_repo_class, mock_session_factory):
    # Setup database & session mocks
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
    mock_session_factory.return_value = MagicMock(return_value=mock_session)

    # Setup repository mock
    mock_repo = MagicMock()
    mock_notification = Notification.create(
        recipient_id=uuid.uuid4(),
        channel=NotificationChannel.EMAIL,
        title="Task Test",
        body="Body",
    )
    mock_repo.get_by_id = AsyncMock(return_value=mock_notification)
    mock_repo.update = AsyncMock()
    mock_repo_class.return_value = mock_repo

    # Setup dispatcher mock
    mock_dispatcher_instance = MagicMock()
    mock_dispatcher_instance.dispatch = AsyncMock()
    mock_dispatcher_class.return_value = mock_dispatcher_instance

    # Run celery task directly using its async implementation
    notification_id = mock_notification.id
    await send_notification_async(str(notification_id))

    # Assertions
    mock_repo.get_by_id.assert_called_once_with(notification_id)
    mock_dispatcher_instance.dispatch.assert_called_once_with(mock_notification)
    mock_repo.update.assert_called_once_with(mock_notification)
    assert mock_notification.status == NotificationStatus.SENT
    mock_session.commit.assert_called_once()


# --- Event Handlers Tests ---


@pytest.mark.unit
@pytest.mark.asyncio
@patch("modules.notifications.event_handlers.SendNotificationHandler")
@patch("modules.notifications.event_handlers.get_session_factory")
async def test_handle_order_placed(mock_session_factory, mock_handler_class):
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
    mock_session_factory.return_value = MagicMock(return_value=mock_session)

    mock_handler_instance = MagicMock()
    mock_handler_instance.handle = AsyncMock()
    mock_handler_class.return_value = mock_handler_instance

    event = MagicMock()
    event.aggregate_id = uuid.uuid4()
    event.customer_id = uuid.uuid4()

    await handle_order_placed(event)

    mock_handler_instance.handle.assert_called_once()
    cmd = mock_handler_instance.handle.call_args[0][0]
    assert cmd.recipient_id == event.customer_id
    assert cmd.channel == NotificationChannel.EMAIL
    assert "placed" in cmd.body


@pytest.mark.unit
@pytest.mark.asyncio
@patch("modules.notifications.event_handlers.SendNotificationHandler")
@patch("modules.notifications.event_handlers.get_session_factory")
async def test_handle_order_confirmed(mock_session_factory, mock_handler_class):
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
    mock_result = MagicMock()
    customer_id = uuid.uuid4()
    mock_result.first.return_value = (customer_id,)
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session_factory.return_value = MagicMock(return_value=mock_session)

    mock_handler_instance = MagicMock()
    mock_handler_instance.handle = AsyncMock()
    mock_handler_class.return_value = mock_handler_instance

    event = MagicMock()
    event.aggregate_id = uuid.uuid4()

    await handle_order_confirmed(event)

    mock_handler_instance.handle.assert_called_once()
    cmd = mock_handler_instance.handle.call_args[0][0]
    assert cmd.recipient_id == customer_id
    assert cmd.channel == NotificationChannel.EMAIL
    assert "confirmed" in cmd.body


@pytest.mark.unit
@pytest.mark.asyncio
@patch("modules.notifications.event_handlers.SendNotificationHandler")
@patch("modules.notifications.event_handlers.get_session_factory")
async def test_handle_delivery_completed(mock_session_factory, mock_handler_class):
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
    mock_result = MagicMock()
    customer_id = uuid.uuid4()
    mock_result.first.return_value = (customer_id,)
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session_factory.return_value = MagicMock(return_value=mock_session)

    mock_handler_instance = MagicMock()
    mock_handler_instance.handle = AsyncMock()
    mock_handler_class.return_value = mock_handler_instance

    event = MagicMock()
    event.order_id = uuid.uuid4()

    await handle_delivery_completed(event)

    mock_handler_instance.handle.assert_called_once()
    cmd = mock_handler_instance.handle.call_args[0][0]
    assert cmd.recipient_id == customer_id
    assert cmd.channel == NotificationChannel.EMAIL
    assert "delivered" in cmd.body


@pytest.mark.unit
@pytest.mark.asyncio
@patch("modules.notifications.event_handlers.SendNotificationHandler")
@patch("modules.notifications.event_handlers.get_session_factory")
async def test_handle_partner_assigned(mock_session_factory, mock_handler_class):
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
    mock_result = MagicMock()
    order_id = uuid.uuid4()
    customer_id = uuid.uuid4()
    partner_name = "Speedy Rider"
    mock_result.first.return_value = (order_id, customer_id, partner_name)
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session_factory.return_value = MagicMock(return_value=mock_session)

    mock_handler_instance = MagicMock()
    mock_handler_instance.handle = AsyncMock()
    mock_handler_class.return_value = mock_handler_instance

    event = MagicMock()
    event.delivery_id = uuid.uuid4()
    event.partner_id = uuid.uuid4()

    await handle_partner_assigned(event)

    # Note: handle_partner_assigned dispatches two notifications (one to customer, one to partner)
    assert mock_handler_instance.handle.call_count == 2

    first_cmd = mock_handler_instance.handle.call_args_list[0][0][0]
    assert first_cmd.recipient_id == customer_id
    assert first_cmd.channel == NotificationChannel.EMAIL
    assert partner_name in first_cmd.body

    second_cmd = mock_handler_instance.handle.call_args_list[1][0][0]
    assert second_cmd.recipient_id == event.partner_id
    assert second_cmd.channel == NotificationChannel.SMS
    assert partner_name in second_cmd.body

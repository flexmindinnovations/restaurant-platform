from typing import Any

from modules.users.application.commands.create_profile import (
    CreateProfileCommand,
    CreateProfileHandler,
    parse_names_from_email,
)
from modules.users.infrastructure.repositories.user_repository import SqlAlchemyUserRepository
from shared.infrastructure.database import get_session_factory
from shared.infrastructure.event_bus import InMemoryEventBus, get_event_bus
from shared.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


async def handle_account_created(event: Any) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        user_repo = SqlAlchemyUserRepository(session)
        event_bus = get_event_bus()
        uow = SqlAlchemyUnitOfWork(session, event_bus)
        handler = CreateProfileHandler(user_repo, uow)

        first_name, last_name = parse_names_from_email(event.email)
        command = CreateProfileCommand(
            account_id=event.aggregate_id,
            first_name=first_name,
            last_name=last_name,
        )
        await handler.handle(command)


def register_event_handlers(event_bus: InMemoryEventBus) -> None:
    event_bus.subscribe_by_name("AccountCreated", handle_account_created)

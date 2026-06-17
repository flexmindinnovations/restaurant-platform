from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session
from modules.users.application.commands.create_profile import CreateProfileHandler
from modules.users.application.commands.update_profile import UpdateProfileHandler
from modules.users.application.queries.get_profile import GetProfileHandler
from modules.users.infrastructure.repositories.user_repository import SqlAlchemyUserRepository
from shared.infrastructure.event_bus import get_event_bus
from shared.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(session)


def get_uow(session: AsyncSession = Depends(get_db_session)) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session, get_event_bus())


def get_create_profile_handler(
    user_repo: SqlAlchemyUserRepository = Depends(get_user_repository),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> CreateProfileHandler:
    return CreateProfileHandler(user_repo, uow)


def get_update_profile_handler(
    user_repo: SqlAlchemyUserRepository = Depends(get_user_repository),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> UpdateProfileHandler:
    return UpdateProfileHandler(user_repo, uow)


def get_profile_query_handler(
    user_repo: SqlAlchemyUserRepository = Depends(get_user_repository),
) -> GetProfileHandler:
    return GetProfileHandler(user_repo)

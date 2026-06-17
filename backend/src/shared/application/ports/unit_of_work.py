from abc import ABC, abstractmethod
from typing import Self

from shared.domain.entity import AggregateRoot


class AbstractUnitOfWork(ABC):
    def __init__(self) -> None:
        self._aggregates: list[AggregateRoot] = []

    def register_aggregate(self, aggregate: AggregateRoot) -> None:
        self._aggregates.append(aggregate)

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type: type | None, exc_val: Exception | None, exc_tb: object) -> None:
        if exc_type is not None:
            await self.rollback()

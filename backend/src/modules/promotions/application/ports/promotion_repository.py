import abc
import uuid

from modules.promotions.domain.entities.coupon_usage import CouponUsage
from modules.promotions.domain.entities.promotion import Promotion


class PromotionRepository(abc.ABC):
    @abc.abstractmethod
    async def add(self, promotion: Promotion) -> None:
        pass

    @abc.abstractmethod
    async def get_by_id(self, promotion_id: uuid.UUID) -> Promotion | None:
        pass

    @abc.abstractmethod
    async def get_by_code(self, code: str) -> Promotion | None:
        pass

    @abc.abstractmethod
    async def update(self, promotion: Promotion) -> None:
        pass

    @abc.abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 10) -> tuple[list[Promotion], int]:
        pass

    @abc.abstractmethod
    async def list_available(self, skip: int = 0, limit: int = 10) -> tuple[list[Promotion], int]:
        pass

    @abc.abstractmethod
    async def add_usage(self, usage: CouponUsage) -> None:
        pass

    @abc.abstractmethod
    async def count_customer_usage(self, promotion_id: uuid.UUID, customer_id: uuid.UUID) -> int:
        pass

import abc
import uuid
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class MenuItemDTO:
    id: uuid.UUID
    restaurant_id: uuid.UUID
    name: str
    price_amount: Decimal
    price_currency: str
    is_available: bool


class MenuService(abc.ABC):
    @abc.abstractmethod
    async def get_menu_item(self, menu_item_id: uuid.UUID) -> MenuItemDTO | None:
        pass

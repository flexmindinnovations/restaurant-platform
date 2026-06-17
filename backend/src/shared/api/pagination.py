from dataclasses import dataclass


@dataclass
class PageParams:
    page: int = 1
    page_size: int = 20
    max_page_size: int = 100

    def __post_init__(self) -> None:
        if self.page < 1:
            self.page = 1
        if self.page_size < 1:
            self.page_size = 20
        if self.page_size > self.max_page_size:
            self.page_size = self.max_page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


@dataclass
class CursorParams:
    cursor: str | None = None
    limit: int = 20
    max_limit: int = 100

    def __post_init__(self) -> None:
        if self.limit < 1:
            self.limit = 20
        if self.limit > self.max_limit:
            self.limit = self.max_limit

from dataclasses import dataclass

from pydantic import BaseModel, Field


@dataclass
class PageParams:
    page: int = 1
    page_size: int = 20
    max_page_size: int = 100

    def __post_init__(self) -> None:
        self.page = max(self.page, 1)
        if self.page_size < 1:
            self.page_size = 20
        self.page_size = min(self.page_size, self.max_page_size)

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
        self.limit = min(self.limit, self.max_limit)


# Pydantic Schemas for API Input/Output Validation
class OffsetPaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number, 1-indexed")
    page_size: int = Field(default=20, ge=1, le=100, description="Number of items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PageResponse[T](BaseModel):
    items: list[T]
    total: int
    page: int
    page_size: int


class CursorPaginationParams(BaseModel):
    cursor: str | None = Field(default=None, description="Cursor for the next page")
    limit: int = Field(default=20, ge=1, le=100, description="Limit of items to return")


class CursorPageResponse[T](BaseModel):
    items: list[T]
    next_cursor: str | None = None
    has_more: bool

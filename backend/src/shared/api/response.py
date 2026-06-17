from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseEnvelope(BaseModel, Generic[T]):
    data: T
    meta: dict = Field(default_factory=dict)

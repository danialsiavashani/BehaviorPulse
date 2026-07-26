from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number, starting at 1"),
        page_size: int = Query(8, ge=1, le=100, description="Items per page, max 100"),
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size
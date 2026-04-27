from unittest import skip

from fastapi import Query
from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar("T")


class PostPagination(BaseModel, Generic[T]):
    total: int
    pages: int
    page: int
    size: int
    items: List[T]


async def pagination(
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(10, ge=1, le=100, description="Items per page")
):
    skip = (page - 1) * size
    return {"skip": skip, "limit": size, "page": page}


async def get_total_pages(
        total, size
):
    return int(total / size) + 1

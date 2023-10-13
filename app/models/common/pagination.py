import math
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel


class PageParams(BaseModel):
    page: int = 1
    size: int = 10


T = TypeVar("T")


class PagedResponseSchema(GenericModel, Generic[T]):
    total: int
    total_page: int
    page: int = 1
    size: int = 10
    items: list[Any]


def paginate(page: int, size: int, query: Any) -> PagedResponseSchema:
    paginated_query = query.offset((page - 1) * size).limit(size).all()
    total_records = query.count()
    return PagedResponseSchema(
        total=total_records,
        total_page=max(math.ceil(total_records / size), 1),
        page=page,
        size=size,
        items=paginated_query,
    )

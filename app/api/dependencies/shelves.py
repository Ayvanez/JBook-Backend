from typing import Optional, Type

from fastapi.params import Query

from app.core.const import DEFAULT_SHELF_ORDER_BY, DEFAULT_SHELF_OFFSET, DEFAULT_SHELF_LIMIT
from app.models.schemas.shelves import ShelfFilter


class ShelfFilterManager:
    validation_error = ValueError

    def __init__(self, allowed_sort_values: list[str]):
        self.allowed_sort_values = allowed_sort_values

    def __call__(
            self,
            tags: Optional[str] = None,
            sort_by: Optional[str] = DEFAULT_SHELF_ORDER_BY,
            offset: int = Query(DEFAULT_SHELF_OFFSET, ge=0),
            limit: int = Query(DEFAULT_SHELF_LIMIT, ge=1)
    ) -> ShelfFilter:

        if tags:
            tags = self.split_to_ids(tags, str)

        if sort_by:
            sort_by = self.modify_sort_by(sort_by)

        return ShelfFilter(
            tags=tags,
            sort_by=sort_by,
            limit=limit,
            offset=offset,
        )

    def split_to_ids(self, spl: str, type_: Type[int | str] = int) -> list[int | str]:
        try:
            return list(map(type_, spl.split(',')))
        except TypeError:
            raise self.validation_error('Wrong prams')

    def modify_sort_by(self, value: str) -> str:
        desc = False
        if value.startswith('-'):
            desc = True
            value = value[1:]

        if value not in self.allowed_sort_values:
            raise self.validation_error('sort_by not on of allowed.')

        return f'{value} ASC' if not desc else f'{value} DESC'

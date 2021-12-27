from typing import Optional, Type

from fastapi.params import Query
from pydantic import ValidationError
from starlette.exceptions import HTTPException

from app.core.const import DEFAULT_BOOK_OFFSET, DEFAULT_BOOK_LIMIT, DEFAULT_BOOK_ORDER_BY
from app.models.schemas.books import BooksFilter


class BookFilterManager:
    validation_error = HTTPException

    def __init__(self, allowed_sort_values: list[str]):
        self.allowed_sort_values = allowed_sort_values

    def __call__(
            self,
            tags: Optional[str] = None,
            categories: Optional[str] = None,
            publishers: Optional[str] = None,
            authors: Optional[str] = None,
            sort_by: Optional[str] = DEFAULT_BOOK_ORDER_BY,
            offset: int = Query(DEFAULT_BOOK_OFFSET, ge=0),
            limit: int = Query(DEFAULT_BOOK_LIMIT, ge=1)
    ) -> BooksFilter:

        if tags:
            tags = self.split_to_ids(tags, str)

        if categories:
            categories = self.split_to_ids(categories)

        if publishers:
            publishers = self.split_to_ids(publishers)

        if authors:
            authors = self.split_to_ids(authors)

        if sort_by:
            sort_by = self.modify_sort_by(sort_by)

        return BooksFilter(
            tags=tags,
            authors=authors,
            categories=categories,
            publishers=publishers,
            sort_by=sort_by,
            limit=limit,
            offset=offset,
        )

    def split_to_ids(self, spl: str, type_: Type[int | str] = int) -> list[int | str]:
        try:
            return list(map(type_, spl.split(',')))
        except (TypeError, ValueError):
            raise self.validation_error(status_code=400, detail='Wrong prams')

    def modify_sort_by(self, value: str) -> str:
        desc = False
        if value.startswith('-'):
            desc = True
            value = value[1:]

        if value not in self.allowed_sort_values:
            raise self.validation_error(status_code=400, detail='sort_by not one of allowed.')

        return f'{value} ASC' if not desc else f'{value} DESC'

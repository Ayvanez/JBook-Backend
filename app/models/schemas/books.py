from typing import Optional

from pydantic import Field

from app.core.const import DEFAULT_BOOK_OFFSET, DEFAULT_BOOK_LIMIT
from app.models.domain.books import Book, BookCategory, BookPublisher, BookTag, BookComment, BookAuthor
from app.models.schemas.rwschema import RWSchema


class BookMinimizedForResponse(RWSchema):
    id: int
    name: str


class ListOfBookPublisherInResponse(RWSchema):
    publishers: list[BookPublisher] = Field([])


class ListOfBookAuthorInResponse(RWSchema):
    authors: list[BookAuthor] = Field([])


class BookForResponse(RWSchema, Book):
    tags: list[BookTag] = Field([])


class BookInResponse(RWSchema):
    book: Book


class ListOfMinimizedBooksInResponse(RWSchema):
    books: list[BookMinimizedForResponse]


class ListOfBooksInResponse(RWSchema):
    books: list[BookForResponse]


class ListOfBookCategoriesInResponse(RWSchema):
    categories: list[BookCategory]


class BookRateInCreate(RWSchema):
    rate: int


class BooksFilter(RWSchema):
    tags: Optional[list[str]] = None
    authors: Optional[list[int]] = None
    categories: Optional[list[int]] = None
    publishers: Optional[list[int]] = None
    sort_by: Optional[str] = 'created_at DESC'

    limit: int = Field(DEFAULT_BOOK_LIMIT, ge=1)
    offset: int = Field(DEFAULT_BOOK_OFFSET, ge=0)

import datetime
from typing import Optional
from uuid import UUID

from app.models.common import DateTimeModelMixin, IDModelMixin
from app.models.domain.books import Book, BookMinimized
from app.models.domain.users import User
from app.models.domain.rwmodel import RWModel


class ShelfTag(RWModel):
    name: str


class BookInShelf(IDModelMixin, RWModel):
    book: BookMinimized
    tags: list[ShelfTag]


class ShelfImage(IDModelMixin, RWModel):
    src: str
    alt_text: str


class Shelf(RWModel):
    books_in_shelf: list[BookInShelf]
    uid: UUID
    name: str
    description: str
    type: str
    avatar: Optional[ShelfImage]
    user: User
    tags: list[ShelfTag]
    created_at: datetime.datetime
    updated_at: datetime.datetime

import datetime

from app.models.common import DateTimeModelMixin, IDModelMixin
from app.models.domain.books import Book
from app.models.domain.users import User
from app.models.domain.rwmodel import RWModel


class BookInShelf(IDModelMixin, RWModel):
    book: Book
    tags: list[str]


class ShelfImage(IDModelMixin, RWModel):
    src: str
    alt_text: str


class Shelf(DateTimeModelMixin, RWModel):
    books_in_shelf: list[BookInShelf]
    uid: str
    name: str
    description: str
    type: str
    avatar: ShelfImage
    user: User
    tags: list[str]
    created_at: datetime
    updated_at: datetime

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.models.domain.shelves import Shelf, ShelfImage, ShelfTag, BookInShelf
from app.models.domain.users import User
from app.models.schemas.rwschema import RWSchema

DEFAULT_SHELF_LIMIT = 20
DEFAULT_SHELF_OFFSET = 0

BookId = int


class ShelfForResponse(RWSchema, Shelf):
    tags: list[ShelfTag] = Field([])


class ShelfInResponse(RWSchema):
    shelf: ShelfForResponse


class ListOfShelvesForResponse(RWSchema):
    uid: UUID
    name: str
    description: str
    type: str
    avatar: Optional[ShelfImage]
    user: User
    rate: Optional[float]
    user_rate: Optional[int]
    books_in_shelf: list[BookInShelf]
    tags: list[ShelfTag]
    created_at: datetime
    updated_at: datetime


class ListOfShelvesInResponse(RWSchema):
    shelves: list[ListOfShelvesForResponse]


class ShelfForCreate(RWSchema):
    name: str
    description: str
    type: str
    tags: list[str]
    books: list[BookId]


class ShelfInCreate(RWSchema):
    shelf: ShelfForCreate


class ShelfRateForResponse(RWSchema):
    rate: int = Field(ge=1, le=5)
    rated_at: datetime


class ShelfRateInResponse(RWSchema):
    rate: ShelfRateForResponse


class ShelfRateInCreate(RWSchema):
    rate: int = Field(ge=1, le=5)


class BookInShelfInResponse(RWSchema):
    book_in_shelf: BookInShelf


class BookInShelfInCreate(RWSchema):
    book_id: int


class BookInShelfInUpdate(RWSchema):
    tags: list[str]


class ShelfFilter(RWSchema):
    tags: Optional[list[str]] = None
    sort_by: Optional[str] = 'created_at DESC'

    limit: int = Field(DEFAULT_SHELF_LIMIT, ge=1)
    offset: int = Field(DEFAULT_SHELF_OFFSET, ge=0)

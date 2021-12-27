from datetime import datetime
from typing import Optional

from pydantic import Field

from app.models.domain.shelves import Shelf, ShelfImage
from app.models.domain.users import User
from app.models.schemas.rwschema import RWSchema

DEFAULT_SHELF_LIMIT = 20
DEFAULT_SHELF_OFFSET = 0

BookId = int


class ShelfForResponse(RWSchema, Shelf):
    tags: list[str] = Field([])


class ShelfInResponse(RWSchema):
    shelf: ShelfForResponse


class ListOfShelvesForResponse(RWSchema):
    uid: str
    name: str
    description: str
    type: str
    avatar: ShelfImage
    user: User
    tags: list[str]
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

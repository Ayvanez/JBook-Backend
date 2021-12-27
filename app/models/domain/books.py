import datetime
from typing import List, Optional

from app.models.common import DateTimeModelMixin, IDModelMixin
from app.models.domain.users import User
from app.models.domain.rwmodel import RWModel


class BookTag(RWModel):
    name: str


class BookCategory(IDModelMixin, RWModel):
    name: str


class BookPublisher(IDModelMixin, RWModel):
    name: str


class BookAuthor(IDModelMixin, RWModel):
    name: str


class BookImage(IDModelMixin, RWModel):
    src: str
    alt_text: str
    is_main: bool


class Book(IDModelMixin, DateTimeModelMixin, RWModel):
    id: str
    title: str
    description: Optional[str]
    annotation: Optional[str]
    authors: list[BookAuthor]
    publisher: Optional[BookPublisher]
    tags: List[BookTag]
    categories: List[BookCategory]
    rate: Optional[float]
    user_rate: Optional[int]

    images: List[BookImage]


class BookComment(IDModelMixin, RWModel):
    user: User
    book: Book
    pub_date: datetime.datetime
    content: str

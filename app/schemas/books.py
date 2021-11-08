from typing import Optional

from pydantic import BaseModel


class BookAuthor(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class BookCategory(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class PublishingHouse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class BookBase(BaseModel):
    id: Optional[int]
    title: Optional[str]
    description: Optional[str]
    publisher: Optional[PublishingHouse]

    class Config:
        orm_mode = True


class BookDetail(BookBase):
    categories: Optional[list[BookCategory]]
    authors: Optional[list[BookAuthor]]

    class Config:
        orm_mode = True

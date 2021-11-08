from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.future import select
from sqlalchemy.orm import Session, load_only, raiseload
from sqlalchemy.orm import selectinload

from app.dependencies.db import get_db
import app.models as model
import app.schemas as schema

router = APIRouter(
    prefix="/books",
    tags=["books"],
    responses={404: {"description": "Not found"}},
)


@router.get('/', response_model=list[schema.BookBase])
async def get_books(
        categories: Optional[str] = Query(None),
        authors: Optional[str] = Query(None),
        publishers: Optional[str] = Query(None),
        db: Session = Depends(get_db)):
    query = select(model.Book).options(
        selectinload(model.Book.categories),
        selectinload(model.Book.authors),
        selectinload(model.Book.publisher)
    )

    if categories:
        categories = map(int, categories.split(','))
        query = query.filter(model.Book.categories.any(model.BookCategory.id.in_(categories)))
    if authors:
        authors = map(int, authors.split(','))
        query = query.filter(model.Book.authors.any(model.BookAuthor.id.in_(authors)))
    if publishers:
        publishers = map(int, publishers.split(','))
        query = query.where(model.Book.publisher_id.in_(publishers))

    query = query.options(load_only(model.Book.id, model.Book.title, model.Book.description),
                          selectinload(model.Book.publisher))
    books = (await db.execute(query)).scalars().all()
    return books


@router.get('/categories', response_model=list[schema.BookCategory])
async def get_categories(db: Session = Depends(get_db)):
    query = select(model.BookCategory)
    categories = (await db.execute(query)).scalars().all()
    return categories


@router.get('/{book_id}', response_model=schema.BookDetail)
async def get_book(book_id: int, db: Session = Depends(get_db)):
    book = (await db.execute(
        select(model.Book)
            .where(model.Book.id == book_id)
            .options(
            selectinload(model.Book.categories),
            selectinload(model.Book.authors),
            selectinload(model.Book.publisher)
        )
    )).first()[0]
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

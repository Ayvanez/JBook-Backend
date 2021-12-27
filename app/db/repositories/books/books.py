from typing import Optional

from sqlalchemy import func, text, desc, delete
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.const import DEFAULT_ORDER_BY, DEFAULT_BOOK_OFFSET, DEFAULT_BOOK_LIMIT
from app.db.queries.tables import User, BookComment, BookRate
from app.db.repositories.base import BaseRepository
from app.db.queries import tables as models

from app.models.domain.books import Book


class BookRepository(BaseRepository):
    async def filter_books(
            self,
            tags: Optional[list[str]] = None,
            categories: Optional[list[int]] = None,
            publishers: Optional[list[int]] = None,
            authors: Optional[list[int]] = None,
            user: Optional[User] = None,
            sort_by: Optional[str] = DEFAULT_ORDER_BY,
            offset=DEFAULT_BOOK_OFFSET,
            limit=DEFAULT_BOOK_LIMIT) -> list[Book]:

        user_id = user.id if user else None

        user_rate_query = select(models.BookRate.book_id, models.BookRate.rate.label('userRate')) \
            .filter(models.BookRate.user_id == user_id).cte()

        rate_query = select(models.BookRate.book_id, func.avg(models.BookRate.rate).label('rate')) \
            .group_by(models.BookRate.book_id).cte()

        query = select(models.Book, rate_query.c.rate, user_rate_query.c.userRate) \
            .options(
            selectinload(models.Book.categories),
            selectinload(models.Book.authors),
            selectinload(models.Book.publisher),
            selectinload(models.Book.tags),
            selectinload(models.Book.images),
        )

        if categories:
            query = query.filter(models.Book.categories.any(models.BookCategory.id.in_(categories)))
        if authors:
            query = query.filter(models.Book.authors.any(models.BookAuthor.id.in_(authors)))
        if publishers:
            query = query.where(models.Book.publisher_id.in_(publishers))
        if tags:
            query = query.filter(models.Book.tags.any(models.BookTag.name.in_(tags)))
        query = query.outerjoin(user_rate_query)
        query = query.outerjoin(rate_query)
        query = query.order_by(text(sort_by)).limit(limit).offset(offset)
        raw_books = (await self.session.execute(query)).all()

        books = []
        for book in raw_books:
            book[0].rate = book[1]
            book[0].user_rate = book[2]
            books.append(book[0])

        return books

    async def get_book_by_id(self, book_id: int, user: Optional[User] = None) -> Optional[Book]:

        user_id = user.id if user else None

        user_rate_query = select(models.BookRate.book_id, models.BookRate.rate.label('userRate')) \
            .filter(models.BookRate.user_id == user_id) \
            .filter(models.BookRate.book_id == book_id) \
            .cte()

        rate_query = select(models.BookRate.book_id, func.avg(models.BookRate.rate).label('rate')) \
            .filter(models.BookRate.book_id == book_id) \
            .group_by(models.BookRate.book_id) \
            .cte()

        query = select(models.Book, rate_query.c.rate, user_rate_query.c.userRate).options(
            selectinload(models.Book.categories),
            selectinload(models.Book.authors),
            selectinload(models.Book.publisher),
            selectinload(models.Book.tags),
            selectinload(models.Book.images),
        ).filter(models.Book.id == book_id)

        query = query.outerjoin(user_rate_query)
        query = query.outerjoin(rate_query)

        book_raw = (await self.session.execute(query)).first()
        if book_raw[0] is None:
            return None
        book_raw[0].rate = book_raw[1]
        book_raw[0].user_rate = book_raw[2]

        return book_raw[0]

    async def get_comments_by_book_id(self, book_id):
        query = select(models.BookComment) \
            .filter(models.BookComment.book_id == book_id) \
            .order_by(desc(models.BookComment.pub_date))
        return (await self.session.execute(query)).scalars().all()

    async def create_comment(self, user: User, book_id: int, content: str):
        async with self.session.begin() as session:
            comment = BookComment(user_id=user.id, book_id=book_id, content=content)
            session.add(comment)

    async def delete_comment(self, user: User, book_id: int):
        async with self.session.begin() as session:
            stmt = delete(models.BookComment) \
                .where(models.BookComment.user_id == user.id & models.BookComment.book_id == book_id)
            session.execute(stmt)

    async def rate_book(self, user: User, book_id: int, rate):
        async with self.session.begin() as session:
            book_rate = BookRate(user_id=user.id, book_id=book_id, rate=rate)
            session.add(book_rate)

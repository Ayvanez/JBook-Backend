from typing import Optional

from sqlalchemy import func, text, desc, delete, insert
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.const import DEFAULT_BOOK_ORDER_BY, DEFAULT_BOOK_OFFSET, DEFAULT_BOOK_LIMIT
from app.db.queries.tables import User, BookComment, BookRate
from app.db.repositories.base import BaseRepository
from app.db.queries import tables as models

from app.models.domain.books import Book


class BookRepository(BaseRepository):

    # Book
    async def filter_books(
            self,
            tags: Optional[list[str]] = None,
            categories: Optional[list[int]] = None,
            publishers: Optional[list[int]] = None,
            authors: Optional[list[int]] = None,
            user: Optional[User] = None,
            sort_by: Optional[str] = DEFAULT_BOOK_ORDER_BY,
            offset=DEFAULT_BOOK_OFFSET,
            limit=DEFAULT_BOOK_LIMIT) -> list[Book]:

        user_uid = user.uid if user else None

        user_rate_query = select(models.BookRate.book_id, models.BookRate.rate.label('userRate')) \
            .filter(models.BookRate.user_uid == user_uid).cte()

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

        raw_books = (await self.session.execute(query)).fetchall()

        books = []
        for book in raw_books:
            book[0].rate = book[1]
            book[0].user_rate = book[2]
            books.append(book[0])

        return books

    async def get_existing_book(self, book_ids: list[int], only_ids=False):
        if only_ids:
            query = select(models.Book.id)
        else:
            query = select(models.Book)
        query = query.filter(models.Book.id.in_(book_ids))
        books = (await self.session.execute(query)).scalars().all()
        return books

    async def get_book_by_id(self, book_id: int, user: Optional[User] = None) -> Optional[Book]:

        user_uid = user.uid if user else None

        user_rate_query = select(models.BookRate.book_id, models.BookRate.rate.label('userRate')) \
            .filter(models.BookRate.user_uid == user_uid) \
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

    async def get_book_instance_by_id(self, book_id) -> Optional[Book]:
        query = select(models.Book) \
            .filter(models.Book.id == book_id)
        return (await self.session.execute(query)).scalars().first()

    # Comments
    async def get_comments(self, book: Book) -> list[BookComment]:
        query = select(models.BookComment) \
            .filter(models.BookComment.book_id == book.id) \
            .order_by(desc(models.BookComment.pub_date)) \
            .options(selectinload(models.BookComment.user))

        return (await self.session.execute(query)).scalars().all()

    async def get_comment_by_id(self, comment_id: int) -> Optional[BookComment]:
        select_query = select(models.BookComment).filter(
            models.BookComment.id == comment_id
        )
        return (await self.session.execute(select_query)).scalars().first()

    async def create_comment(self, user: User, book: Book, content: str):
        insert_query = insert(models.BookComment) \
            .values(user_uid=user.uid, book_id=book.id, content=content) \
            .returning(models.BookComment.id, models.BookComment.content, models.BookComment.pub_date)

        comment_tuple = (await self.session.execute(insert_query)).first()
        comment_obj = models.BookComment(id=comment_tuple[0], content=comment_tuple[1], pub_date=comment_tuple[2])
        comment_obj.user = user

        return comment_obj

    async def delete_comment(self, comment: BookComment):
        delete_query = delete(models.BookComment).filter(
            models.BookComment.id == comment.id
        )
        await self.session.execute(delete_query)

    # Rates
    async def get_rate(self, user: User, book: Book):
        get_query = select(models.BookRate).filter(
            models.BookRate.user_uid == user.uid,
            models.BookRate.book_id == book.id
        )

        book_rate = (await self.session.execute(get_query)).scalars().first()

        return book_rate

    async def rate_book(self, user: User, book: Book, rate: int):
        insert_query = insert(models.BookRate) \
            .values(user_uid=user.uid, book_id=book.id, rate=rate) \
            .returning(models.BookRate.id, models.BookRate.rate, models.BookRate.rated_at)

        rate_tuple = (await self.session.execute(insert_query)).first()
        rate_obj = models.BookRate(rate=rate_tuple[1], rated_at=rate_tuple[2])

        return rate_obj

    async def delete_rate(self, rate: BookRate):
        delete_query = delete(models.BookRate).filter(
            models.BookRate.id == rate.id
        )
        await self.session.execute(delete_query)

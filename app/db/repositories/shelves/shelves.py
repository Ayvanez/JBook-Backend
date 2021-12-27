from typing import Optional
from uuid import UUID

from sqlalchemy import func, text, desc, delete, insert
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.const import DEFAULT_SHELF_LIMIT, DEFAULT_SHELF_OFFSET
from app.db.errors import RequireUser
from app.db.queries import tables as models
from app.db.queries.tables import ShelfComment
from app.db.repositories.base import BaseRepository
from app.db.queries import tables as models
from app.models.domain.shelves import Shelf


class ShelfRepository(BaseRepository):

    async def get_shelf_instance_by_uid(self, shelf_uid: UUID) -> Optional[models.Shelf]:
        query = select(models.Shelf) \
            .filter(models.Shelf.uid == shelf_uid)
        return (await self.session.execute(query)).scalars().first()

    async def get_shelf_by_uid(self, shelf_uid: UUID, user: Optional[models.User] = None) -> Optional[models.Shelf]:
        user_uid = user.uid if user else None

        user_rate_query = select(models.ShelfRate.shelf_uid, models.ShelfRate.rate.label('userRate')) \
            .filter(models.ShelfRate.user_uid == user_uid) \
            .filter(models.ShelfRate.shelf_uid == shelf_uid) \
            .cte()

        rate_query = select(models.ShelfRate.shelf_uid, func.avg(models.ShelfRate.rate).label('rate')) \
            .filter(models.ShelfRate.shelf_uid == shelf_uid) \
            .group_by(models.ShelfRate.shelf_uid) \
            .cte()

        query = select(models.Shelf, rate_query.c.rate, user_rate_query.c.userRate).options(
            selectinload(models.Shelf.tags),
            selectinload(models.Shelf.avatar),
        ).filter(models.Shelf.uid == shelf_uid)

        query = query.outerjoin(user_rate_query)
        query = query.outerjoin(rate_query)

        shelf_raw = (await self.session.execute(query)).first()
        if shelf_raw[0] is None:
            return None
        shelf_raw[0].rate = shelf_raw[1]
        shelf_raw[0].user_rate = shelf_raw[2]

        return shelf_raw[0]

    async def filter_shelves(
            self,
            tags: Optional[list[str]],
            sort_by: Optional[str],
            _type: str = 'public',
            limit: Optional[int] = DEFAULT_SHELF_LIMIT,
            offset: Optional[int] = DEFAULT_SHELF_OFFSET,
            user: Optional[models.User] = None,
            only_user: bool = False

    ) -> list[models.Shelf]:
        user_uid = user.uid if user else None

        user_rate_query = select(models.ShelfRate.shelf_uid, models.ShelfRate.rate.label('userRate')) \
            .filter(models.ShelfRate.user_uid == user_uid) \
            .cte()

        rate_query = select(models.ShelfRate.shelf_uid, func.avg(models.ShelfRate.rate).label('rate')) \
            .group_by(models.ShelfRate.shelf_uid) \
            .cte()

        query = select(models.Shelf, rate_query.c.rate, user_rate_query.c.userRate).options(
            selectinload(models.Shelf.tags),
            selectinload(models.Shelf.avatar),
        )

        if tags:
            query = query.filter(models.Shelf.tags.any(models.ShelfTag.name.in_(tags)))

        query = query.order_by(text(sort_by)).limit(limit).offset(offset)

        query = query.outerjoin(user_rate_query)
        query = query.outerjoin(rate_query)

        if only_user:
            if not user:
                raise RequireUser("When only_user passed, user should be included in query")

            query = query.filter(models.Shelf.user_uid == user.uid)

        raw_shelves = (await self.session.execute(query)).fetchall()

        shelves = []
        for shelf in raw_shelves:
            shelf[0].rate = shelf[1]
            shelf[0].user_rate = shelf[2]
            shelves.append(shelf[0])

        return shelves

    async def create_shelf(
            self,
            name: str,
            description: Optional[str],
            _type: str,
            tags: list[str],
            book_ids: list[int],
            user: models.User
    ) -> models.Shelf:
        tags = set(tags)

        shelf_tags_query = select(models.ShelfTag).filter(models.ShelfTag.name.in_(tags))
        shelf_tags_created = (await self.session.execute(shelf_tags_query)).scalars().all()

        tags_to_create = tags - set(tag.name for tag in shelf_tags_created)

        tags_objs = [models.ShelfTag(name=name) for name in tags_to_create]
        books_in_shelf = [models.BookInShelf(book_id=book_id) for book_id in book_ids]

        shelf = models.Shelf(name=name, description=description, type=_type, tags=tags_objs, user_uid=user.uid,
                             books_in_shelf=books_in_shelf)
        shelf.tags.extend(shelf_tags_created)
        self.session.add(shelf)
        await self.session.flush()
        await self.session.refresh(shelf)

        return shelf

    # Rates
    async def get_rate(self, shelf: models.Shelf, user: models.User) -> models.ShelfRate:
        get_query = select(models.ShelfRate).filter(
            models.ShelfRate.user_uid == user.uid,
            models.ShelfRate.shelf_uid == shelf.uid
        )

        shelf_rate = (await self.session.execute(get_query)).scalars().first()

        return shelf_rate

    async def rate_shelf(self, shelf: models.Shelf, user: models.User, rate: int) -> models.ShelfRate:
        insert_query = insert(models.ShelfRate) \
            .values(user_uid=user.uid, shelf_uid=shelf.uid, rate=rate) \
            .returning(models.ShelfRate.id, models.ShelfRate.rate, models.ShelfRate.rated_at)

        rate_tuple = (await self.session.execute(insert_query)).first()
        rate_obj = models.ShelfRate(rate=rate_tuple[1], rated_at=rate_tuple[2])

        return rate_obj

    async def delete_rate(self, rate):
        delete_query = delete(models.ShelfRate).filter(
            models.ShelfRate.id == rate.id
        )

        await self.session.execute(delete_query)

    # Comments
    async def get_comments(self, shelf: models.Shelf) -> list[models.ShelfComment]:
        query = select(models.ShelfComment) \
            .filter(models.ShelfComment.shelf_uid == shelf.uid) \
            .order_by(desc(models.ShelfComment.pub_date)) \
            .options(selectinload(models.ShelfComment.user))

        return (await self.session.execute(query)).scalars().all()

    async def get_comment_by_id(self, comment_id: int) -> models.ShelfComment:
        select_query = select(models.ShelfComment).filter(
            models.ShelfComment.id == comment_id
        )
        return (await self.session.execute(select_query)).scalars().first()

    async def create_comment(self, user: models.User, shelf: models.Shelf, content: str) -> models.ShelfComment:
        insert_query = insert(models.ShelfComment) \
            .values(user_uid=user.uid, shelf_uid=shelf.uid, content=content) \
            .returning(models.ShelfComment.id, models.ShelfComment.content, models.ShelfComment.pub_date)

        comment_tuple = (await self.session.execute(insert_query)).first()
        comment_obj = models.ShelfComment(id=comment_tuple[0], content=comment_tuple[1], pub_date=comment_tuple[2])
        comment_obj.user = user

        return comment_obj

    async def delete_comment(self, comment: ShelfComment):
        delete_query = delete(models.ShelfComment).filter(
            models.ShelfComment.id == comment.id
        )
        await self.session.execute(delete_query)

    # Books
    async def get_book_in_shelf_by_id(self, book_in_shelf_id: int) -> models.BookInShelf:
        query = select(models.BookInShelf) \
            .filter(models.BookInShelf.id == book_in_shelf_id)
        return (await self.session.execute(query)).scalars().first()

    async def get_book_in_shelf_by_book(self, shelf: models.Shelf, book: models.Book):
        query = select(models.BookInShelf) \
            .filter(
            models.BookInShelf.book_uid == shelf.uid,
            models.BookInShelf.book_id == book.id
        )
        return (await self.session.execute(query)).scalars().first()

    async def add_book(self, shelf: models.Shelf, book: models.Book) -> models.BookInShelf:
        book_in_shelf = models.BookInShelf(
            shelf_uid=shelf.uid,
            book_id=book.id
        )
        self.session.add(book_in_shelf)
        await self.session.flush()
        await self.session.refresh(book_in_shelf)

        return book_in_shelf

    async def delete_book_in_shelf(self, book_in_shelf: models.BookInShelf):
        delete_query = delete(models.BookInShelf).filter(
            models.BookInShelf.id == book_in_shelf.id
        )
        await self.session.execute(delete_query)

    async def change_book_in_shelf(self, book_in_shelf: models.BookInShelf, tags: set[str]) -> models.BookInShelf:
        book_in_shelf.tags = []
        tags_obj = [models.BookInShelfTag(name=tag) for tag in tags]
        book_in_shelf.tags = tags_obj

        await self.session.flush()
        await self.session.refresh(book_in_shelf)

        return book_in_shelf

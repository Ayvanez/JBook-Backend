from sqlalchemy.future import select

from app.db.repositories.base import BaseRepository
from app.db.queries.tables import BookAuthor as BookAuthorTable

from app.models.domain.books import BookAuthor


class BookAuthorRepository(BaseRepository):
    async def get_all_authors(self) -> list[BookAuthor]:
        authors = (await self.session.execute(select(BookAuthorTable))).scalars().all()
        return authors

from sqlalchemy.future import select

from app.db.repositories.base import BaseRepository
from app.db.queries.tables import BookCategory as BookCategoryTable

from app.models.domain.books import BookCategory


class BookCategoryRepository(BaseRepository):
    async def get_all_categories(self) -> list[BookCategory]:
        categories = (await self.session.execute(select(BookCategoryTable))).scalars().all()
        return categories

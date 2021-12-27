from typing import List

from sqlalchemy.future import select

from app.db.repositories.base import BaseRepository
from app.db.queries.tables import BookPublisher as BookPublisherTable

from app.models.domain.books import BookPublisher


class BookPublisherRepository(BaseRepository):
    async def get_all_publishers(self) -> List[BookPublisher]:
        publishers = (await self.session.execute(select(BookPublisherTable))).scalars().all()
        return publishers

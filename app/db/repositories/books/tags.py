from typing import List, Sequence

from sqlalchemy.future import select

from app.db.repositories.base import BaseRepository
from app.db.queries.tables import BookTag


class BookTagsRepository(BaseRepository):
    async def get_all_book_tags(self) -> List[str]:
        tags = (await self.session.execute(select(BookTag))).scalars().all()
        return [tag.name for tag in tags]



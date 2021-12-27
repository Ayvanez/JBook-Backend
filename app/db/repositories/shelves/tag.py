from sqlalchemy.future import select

from app.db.repositories.base import BaseRepository
from app.db.queries.tables import ShelfTag


class ShelfTagsRepository(BaseRepository):
    async def get_all_shelf_tags(self) -> list[str]:
        tags = (await self.session.execute(select(ShelfTag))).scalars().all()
        return [tag.name for tag in tags]



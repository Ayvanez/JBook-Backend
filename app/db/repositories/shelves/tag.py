from sqlalchemy.future import select

from app.db.repositories.base import BaseRepository
from app.db.queries import tables as models


class ShelfTagsRepository(BaseRepository):
    async def get_all_shelf_tags(self) -> list[str]:
        tags = (await self.session.execute(select(models.ShelfTag))).scalars().all()
        return [tag.name for tag in tags]



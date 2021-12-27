from typing import Optional

from sqlalchemy import insert
from sqlalchemy.future import select

from app.db.queries.tables import User
from app.models.domain import users as users_
from app.db.repositories.base import BaseRepository
from app.db.queries import tables as models


class UsersRepository(BaseRepository):
    async def get_or_create_user(self, user_uid: str, first_name: Optional[str] = None,
                                 surname: Optional[str] = None) -> User:
        get_query = select(models.User).filter(models.User.uid == user_uid)
        user = (await self.session.execute(get_query)).scalars().first()
        if user is None:
            _user = users_.User(uid=user_uid, first_name=first_name, surname=surname)
            insert_query = insert(models.User).values(uid=user_uid, first_name=first_name, surname=surname)
            await self.session.execute(insert_query)
            await self.session.commit()
            user = _user

        return user

    async def get_user_id_exists(self, user_uid: Optional[str]) -> Optional[User]:
        if user_uid is None:
            return None
        get_query = select(models.User).filter(models.User.uid == user_uid)
        user = (await self.session.execute(get_query)).scalars().first()
        return user

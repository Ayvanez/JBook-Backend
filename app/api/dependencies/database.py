from typing import Callable, Type, Awaitable
from fastapi import Depends
from sqlalchemy.orm import sessionmaker as SessionMaker
from starlette.requests import Request

from app.db.repositories.base import BaseRepository


def _get_session_maker(request: Request) -> SessionMaker:
    return request.app.state.session_maker


def get_repository(
        repo_type: Type[BaseRepository],
) -> Callable[[SessionMaker], BaseRepository]:
    async def _get_repo(
            session_maker: SessionMaker = Depends(_get_session_maker),
    ) -> BaseRepository:
        async with session_maker() as session:
            async with session.begin():
                yield repo_type(session)

    return _get_repo

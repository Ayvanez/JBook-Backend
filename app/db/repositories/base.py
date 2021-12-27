from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.__session = session

    @property
    def session(self) -> AsyncSession:
        return self.__session

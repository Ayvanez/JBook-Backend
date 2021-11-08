from typing import Generator
from app.db.session import SessionLocal


async def get_db() -> Generator:
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()

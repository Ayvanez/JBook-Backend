from fastapi import FastAPI
from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.settings.app import AppSettings


async def configure_sqlalchemy(app: FastAPI, settings: AppSettings) -> None:
    logger.info("Configuring sqlalchemy. database url: {0}", repr(settings.database_url))

    engine = create_async_engine(
        settings.database_url
    )
    app.state.engine = engine
    app.state.session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

    logger.info("sqlalchemy configured")


async def dispose_engine(app: FastAPI) -> None:
    logger.info("Dispose Engine")

    await app.state.engine.dispose()

    logger.info("Engine disposed")

"""
Database module for managing database connections and sessions.

This module provides functions and classes for creating and managing database sessions asynchronously.

Attributes:
    engine (AsyncEngine): The asynchronous engine for the database connection.
    sessionmanager (DatabaseSessionManager): The session maker for creating database sessions.

Classes:
    DatabaseSessionManager: A class for managing database sessions.
"""
import contextlib

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from src.conf.config import config

engine = create_async_engine(config.DB_URL)


class DatabaseSessionManager:
    """
    A class for managing database sessions.

    Attributes:
        _engine (AsyncEngine | None): The asynchronous engine for the database connection.
        _session_maker (async_sessionmaker): The async session maker for creating database sessions.
    """
    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(autoflush=False, autocommit=False,
                                                                     bind=self._engine)

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Context manager for acquiring a database session.

        Yields:
            AsyncSession: An asynchronous database session.

        Raises:
            Exception: If session is not initialized.
        """
        if self._session_maker is None:
            raise Exception(
                "Session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except Exception as err:
            print(err)
            await session.rollback()
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(config.DB_URL)


async def get_db():
    """
    Asynchronous function to get a database session.

    Yields:
        AsyncSession: An asynchronous database session.
    """
    async with sessionmanager.session() as session:
        yield session

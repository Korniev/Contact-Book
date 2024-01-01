import contextlib

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.conf.config import config


class DatabaseSessionManager:
    """
        A class for managing database sessions in an asynchronous context using SQLAlchemy.

        This session manager creates and handles SQLAlchemy sessions for asynchronous database queries.
        It utilizes a context manager for safely opening and closing sessions.

        Attributes:
            _engine (AsyncEngine): An asynchronous engine for connecting to the database.
            _session_maker (async_sessionmaker): A factory for creating new asynchronous sessions.

        Args:
            url (str): The database connection URL.

        Methods:
            session: A context manager for creating and managing database sessions.
    """
    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(autoflush=False, autocommit=False,
                                                                     bind=self._engine)

    @contextlib.asynccontextmanager
    async def session(self):
        if self._session_maker is None:
            raise Exception("Session is not initialized")
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
        An asynchronous generator that provides access to the database session.

        This generator is used in FastAPI routes to obtain and manage database sessions.
        It employs the `DatabaseSessionManager` for creating an asynchronous session,
        ensuring proper session opening and closure.

        Yields:
            AsyncSession: An asynchronous database session for use in API routes.
        """
    async with sessionmanager.session() as session:
        yield session

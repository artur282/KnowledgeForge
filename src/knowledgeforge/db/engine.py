"""Database engine configuration."""


from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


def create_engine(database_url: str) -> async_sessionmaker[AsyncSession]:
    """Create an async SQLAlchemy engine."""
    return create_async_engine(database_url, echo=False)


def get_session_factory(engine):
    """Create a session factory bound to the engine."""
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session(session_factory):
    """Yield an async database session."""
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

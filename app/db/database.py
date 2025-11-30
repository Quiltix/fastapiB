import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user123:qwerty123@localhost:5432/event"
)
engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
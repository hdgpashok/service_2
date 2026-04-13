from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.core.config import Settings

settings = Settings()

engine = create_async_engine(str(settings.postgres_url), echo=False)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


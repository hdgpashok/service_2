import uuid

import pytest
import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer
from src.models.base import Base

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer(
            "postgres:15",
            username="test",
            password="test",
            dbname="test",
    ) as postgres:

        port = postgres.get_exposed_port(5432)

        url = (
            f"postgresql+asyncpg://"
            f"test:test@localhost:{port}/test"
        )

        yield url


@pytest.fixture
async def async_engine(postgres_container):
    engine = create_async_engine(
        postgres_container,
        pool_pre_ping=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def mock_session(async_engine):
    async_session_maker = async_sessionmaker(
        async_engine,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
def user_id():
    return uuid.uuid4()
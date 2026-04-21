import uuid
import asyncio
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.core.dependencies import get_session, get_client
from src.application import get_app
from src.schemas.profile import ProfileCreate
from src.schemas.user import UserCreate, UserOut
from src.models.base import Base
from src.core.redis_cache import CacheService
from src.services.call_api import ClientMainService


app = get_app()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15", username="test", password="test", dbname="test") as postgres:
        port = postgres.get_exposed_port(5432)
        yield f"postgresql+asyncpg://test:test@localhost:{port}/test"


@pytest_asyncio.fixture(scope='session')
async def mock_async_engine(postgres_container):
    engine = create_async_engine(postgres_container)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope='function')
async def mock_session(mock_async_engine):
    async_session_maker = async_sessionmaker(mock_async_engine, expire_on_commit=False)

    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest.fixture(scope="session")
def redis_container():
    with RedisContainer("redis:7-alpine") as container:
        yield container


@pytest_asyncio.fixture(scope="session")
async def redis_client(redis_container):
    from redis.asyncio import Redis

    client = Redis(
        host=redis_container.get_container_host_ip(),
        port=redis_container.get_exposed_port(6379),
        db=0,
        decode_responses=False,
    )
    yield client
    await client.close()


@pytest_asyncio.fixture(scope="function")
async def cache(redis_client):
    return CacheService(redis_client=redis_client)


@pytest_asyncio.fixture(scope='function')
async def mock_client_get(mock_id):
    return {
        "id": mock_id,
        "title": "string",
        "profile": {
            "title": "string",
            "bio": "string",
            "id": mock_id
        }
    }


@pytest_asyncio.fixture(scope='function')
async def mock_call_client(cache, mock_client_get):
    client = AsyncMock(spec=ClientMainService)
    client.cache = cache

    client.user_get_request = AsyncMock(return_value=mock_client_get)
    client.user_post_request = AsyncMock()
    client.user_delete_request = AsyncMock()

    return client


@pytest_asyncio.fixture(scope='function')
async def mock_client(mock_session, mock_call_client):
    app.dependency_overrides[get_session] = lambda: mock_session
    app.dependency_overrides[get_client] = lambda: mock_call_client

    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test/api/v1/users_profiles",
    ) as cli:
        yield cli

    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
def mock_create_profile():
    return ProfileCreate(
        nickname="test",
        title="test",
        bio="test",
    )


@pytest.fixture(scope='session')
def mock_create_user(mock_create_profile):
    return UserCreate(
        first_name="test",
        last_name="test",
        title="test",
        profile=mock_create_profile
    )


@pytest.fixture(scope='session')
def mock_id():
    return uuid.UUID("12345678-1234-5678-1234-567812345678")


@pytest.fixture(scope='session')
def user_out(mock_id, mock_create_user) -> UserOut:
    return UserOut(
        id=mock_id,
        first_name=mock_create_user.first_name,
        last_name=mock_create_user.last_name,
        profile={
            'id': mock_id,
            'nickname': mock_create_user.profile.nickname,
            'title': mock_create_user.profile.title,
            'bio': mock_create_user.profile.bio
        }
    )
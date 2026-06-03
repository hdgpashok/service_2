import asyncio
import uuid
import httpx
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from redis.asyncio import Redis

from testcontainers.core.container import DockerContainer
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.dependencies.client import get_client
from src.dependencies.session import get_session
from src.application import get_app
from src.models.base import Base
from src.core.redis_cache import CacheService
from src.client.call_api import ClientUserService
from src.schemas.profile import ProfileCreate
from src.schemas.user import UserCreate


app = get_app()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15", username="test", password="test", dbname="test_db") as postgres:
        port = postgres.get_exposed_port(5432)
        yield f"postgresql+asyncpg://test:test@localhost:{port}/test_db"


@pytest.fixture(scope="session")
def redis_container():
    with RedisContainer("redis:7-alpine") as container:
        yield container


@pytest_asyncio.fixture(scope="function")
async def service_container_setup(mock_service_url):
    async def _setup(endpoint: str, method: str = "GET", response_json: dict | None = None, status: int = 200):
        payload = {
            "request": {"method": method.upper(), "url": endpoint},
            "response": {
                "status": status,
                "headers": {"Content-Type": "application/json"}
            }
        }
        if response_json:
            payload["response"]["jsonBody"] = response_json

        async with httpx.AsyncClient() as client:
            await client.post(f"{mock_service_url}/__admin/mappings", json=payload)

    yield _setup

    async with httpx.AsyncClient() as client:
        await client.delete(f"{mock_service_url}/__admin/mappings")


@pytest.fixture(scope="session")
def service_container():
    container = DockerContainer("wiremock/wiremock:latest")
    container.with_exposed_ports(8080)
    container.start()
    yield container
    container.stop()


@pytest.fixture(scope="session")
def mock_service_url(service_container):
    host = service_container.get_container_host_ip()
    port = service_container.get_exposed_port(8080)
    return f"http://{host}:{port}"


@pytest_asyncio.fixture(scope="session")
async def mock_async_engine(postgres_container):
    engine = create_async_engine(postgres_container, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def mock_session(mock_async_engine):
    async_session_maker = async_sessionmaker(mock_async_engine, expire_on_commit=False)
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def cache(redis_container):
    redis_client = Redis(
        host=redis_container.get_container_host_ip(),
        port=redis_container.get_exposed_port(6379),
        db=0,
        decode_responses=False,
    )
    cache_service = CacheService(redis_client=redis_client)
    yield cache_service
    await redis_client.close()


@pytest_asyncio.fixture(scope="function")
async def mock_call_client(cache, mock_service_url):
    client = ClientUserService(cache=cache, base_url=mock_service_url)
    yield client
    await client.aclose() if hasattr(client, "aclose") else None


@pytest_asyncio.fixture(scope="function")
async def mock_client(mock_session, mock_call_client):
    app.dependency_overrides[get_session] = lambda: mock_session
    app.dependency_overrides[get_client] = lambda: mock_call_client

    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test/api/v1/users_profiles",
    ) as cli:
        yield cli

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def mock_id():
    return uuid.uuid4()


@pytest.fixture(scope="session")
def mock_create_profile():
    return ProfileCreate(nickname="test", title="test", bio="test")


@pytest.fixture(scope="session")
def mock_create_user(mock_create_profile):
    return UserCreate(
        first_name="test",
        last_name="test",
        title="test",
        profile=mock_create_profile
    )
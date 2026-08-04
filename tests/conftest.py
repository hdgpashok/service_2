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

from src.application import get_app
from src.models.base import Base
from src.session import get_session
from src.dependencies.client import get_client
from src.dependencies.user_service import get_service
from src.client.client_main_user_service import ClientUserService
from src.redis_cache import CacheService
from src.services.user import UserService
from src.services.saga_coordinator import SagaCoordinator
from src.schemas.profile import ProfileCreate
from src.schemas.user import UserCreate


app = get_app()


@pytest.fixture(scope="session")
def postgres_url():
    with PostgresContainer(
            "postgres:15",
            username="test",
            password="test",
            dbname="test_db",
    ) as postgres:
        port = postgres.get_exposed_port(5432)
        yield f"postgresql+asyncpg://test:test@localhost:{port}/test_db"


@pytest.fixture(scope="session")
def redis_container():
    with RedisContainer("redis:7-alpine") as container:
        yield container


@pytest.fixture(scope="session")
def wiremock_container():
    container = DockerContainer("wiremock/wiremock:latest")
    container.with_exposed_ports(8080)
    container.start()
    yield container
    container.stop()


@pytest.fixture(scope="session")
def mock_service_url(wiremock_container):
    host = wiremock_container.get_container_host_ip()
    port = wiremock_container.get_exposed_port(8080)
    return f"http://{host}:{port}"


@pytest_asyncio.fixture
async def engine(postgres_url):
    engine = create_async_engine(postgres_url, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine):
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())

    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest_asyncio.fixture
async def cache(redis_container):
    redis_client = Redis(
        host=redis_container.get_container_host_ip(),
        port=redis_container.get_exposed_port(6379),
        db=0,
        decode_responses=False,
    )
    cache_service = CacheService(redis_client=redis_client)
    yield cache_service
    await redis_client.flushdb()
    await redis_client.aclose()


@pytest_asyncio.fixture
async def wiremock_stub(mock_service_url):
    async def _stub(
            endpoint: str,
            method: str = "GET",
            response_json: dict | None = None,
            status: int = 200,
    ):
        payload = {
            "request": {
                "method": method.upper(),
                "urlPath": endpoint,
            },
            "response": {
                "status": status,
                "headers": {"Content-Type": "application/json"},
                "jsonBody": response_json or {},
            },
        }

        async with httpx.AsyncClient() as client:
            await client.post(f"{mock_service_url}/__admin/mappings", json=payload)

    yield _stub

    async with httpx.AsyncClient() as client:
        await client.delete(f"{mock_service_url}/__admin/mappings")


@pytest_asyncio.fixture
async def external_client(mock_service_url):
    client = ClientUserService(
        base_url=f"{mock_service_url}/api/v1/users_profiles"
    )
    yield client
    await client.client.aclose()


@pytest_asyncio.fixture
async def user_service(cache, external_client):
    coordinator = SagaCoordinator(external_client=external_client)
    return UserService(
        cache=cache,
        client=external_client,
        coordinator=coordinator,
    )


@pytest_asyncio.fixture
async def api_client(session, user_service, external_client):
    app.dependency_overrides[get_session] = lambda: session
    app.dependency_overrides[get_client] = lambda: external_client
    app.dependency_overrides[get_service] = lambda: user_service

    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_id():
    return uuid.uuid4()


@pytest.fixture
def user_create_data():
    return UserCreate(
        first_name="Ivan",
        last_name="Ivanov",
        title="developer",
        profile=ProfileCreate(
            nickname="ivan",
            title="profile_title",
            bio="bio",
        ),
    )


@pytest.fixture
def user_create_payload():
    return {
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "title": "developer",
        "profile": {
            "nickname": "ivan",
            "title": "profile_title",
            "bio": "bio",
        },
    }
import uuid
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from typing import Dict, Any


from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from fastapi.testclient import TestClient
from testcontainers.postgres import PostgresContainer

from src.db import get_session
from src.models.base import Base
from src.models.user import UserModel
from src.models.profile import ProfileModel
from src.schemas.user import UserCreate, UserOut
from src.schemas.profile import ProfileCreate
from src.application import get_app


app = get_app()

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15", username="test", password="test", dbname="test") as postgres:
        port = postgres.get_exposed_port(5432)
        yield f"postgresql+asyncpg://test:test@localhost:{port}/test"


@pytest.fixture
async def async_engine(postgres_container):
    engine = create_async_engine(postgres_container, pool_pre_ping=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def mock_session(async_engine) -> AsyncSession:
    async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
def user_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def profile_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def profile_create_data() -> ProfileCreate:
    return ProfileCreate(
        title="Test Profile",
        bio="Test Bio",
        nickname="test_nick"
    )


@pytest.fixture
def user_create_data(profile_create_data: ProfileCreate) -> UserCreate:
    return UserCreate(
        title="Test User Title",
        first_name="John",
        last_name="Doe",
        profile=profile_create_data
    )


@pytest.fixture
def external_user_data(user_id: uuid.UUID, profile_id: uuid.UUID) -> Dict[str, Any]:
    return {
        'id': str(user_id),
        'title': 'External User Title',
        'profile': {
            'id': str(profile_id),
            'title': 'External Profile Title',
            'bio': 'External Profile Bio'
        }
    }


@pytest.fixture
def profile_model(profile_id: uuid.UUID) -> ProfileModel:
    return ProfileModel(
        id=profile_id,
        nickname="test_nick"
    )


@pytest.fixture
def user_model(user_id: uuid.UUID, profile_model: ProfileModel) -> UserModel:
    user = UserModel(
        id=user_id,
        first_name="John",
        last_name="Doe",
        profile=profile_model
    )
    profile_model.user = user
    return user


@pytest.fixture
def user_out(user_id: uuid.UUID, profile_id: uuid.UUID, user_create_data: UserCreate) -> UserOut:
    return UserOut(
        id=user_id,
        first_name=user_create_data.first_name,
        last_name=user_create_data.last_name,
        profile={
            'id': profile_id,
            'nickname': user_create_data.profile.nickname,
            'title': user_create_data.profile.title,
            'bio': user_create_data.profile.bio
        }
    )


@pytest.fixture
def mock_user_repository():
    with patch('src.services.user.UserRepository') as mock:
        mock.select = AsyncMock()
        mock.create = AsyncMock()
        yield mock


@pytest.fixture
def mock_profile_repository():
    with patch('src.services.user.ProfileRepository') as mock:
        mock.select = AsyncMock()
        yield mock


@pytest.fixture
def mock_api_client():
    with patch('src.services.user.api') as mock:
        mock.user_post_request = AsyncMock()
        mock.user_get_request = AsyncMock()
        yield mock


@pytest.fixture
def mock_client_class():
    with patch('src.services.user.Client') as mock:
        mock.user_delete_request = AsyncMock()
        yield mock


@pytest.fixture
def client_override(mock_session):
    app.dependency_overrides[get_session] = lambda: mock_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


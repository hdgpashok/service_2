import uuid

import pytest

from src.models.profile import ProfileModel
from src.models.user import UserModel
from src.repository.user import UserRepository


@pytest.mark.asyncio
async def test_create_user(mock_session):
    payload_profile = ProfileModel(
        id=uuid.uuid4(),
        nickname="nick"
    )
    payload = UserModel(
        id=uuid.uuid4(),
        first_name="Bob",
        last_name="Karl",
        profile=payload_profile
    )

    user = await UserRepository.create(payload, mock_session)

    assert user.id is not None
    assert user.first_name == "Bob"
    assert user.last_name == 'Karl'
    assert user.profile.nickname == "nick"




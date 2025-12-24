from uuid import UUID

from pydantic import ConfigDict


class ProfileBase:
    title: str
    bio: str
    nickname: str


class ProfileOut(ProfileBase):
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)

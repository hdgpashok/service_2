from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProfileBase(BaseModel):
    nickname: str


class ProfileOut(ProfileBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class ProfileOutput(ProfileBase):
    id: UUID
    title: str
    bio: str


class ProfileCreate(ProfileBase):
    title: str
    bio: str


class ProfileExternal(BaseModel):
    id: UUID
    title: str
    bio: str

    model_config = ConfigDict(from_attributes=True)


class ProfileJoined(ProfileExternal):
    nickname: str


from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProfileBase(BaseModel):
    title: str
    bio: str
    nickname: str


class ProfileOut(ProfileBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class ProfileCreate(ProfileBase):
    pass


class ProfileExternal(BaseModel):
    id: UUID
    title: str
    bio: str

    model_config = ConfigDict(from_attributes=True)

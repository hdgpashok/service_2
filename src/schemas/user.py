from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.schemas.profile import ProfileOut, ProfileCreate, ProfileExternal, ProfileJoined


class UserBase(BaseModel):
    first_name: str
    last_name: str


class UserOut(UserBase):
    id: UUID
    title: str
    bio: str
    profile: ProfileOut

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    title: str
    profile: ProfileCreate

    model_config = ConfigDict(from_attributes=True)


class UserExternal(BaseModel):
    id: UUID
    title: str
    profile: ProfileExternal

    model_config = ConfigDict(from_attributes=True)


class UserJoined(UserBase, UserExternal):
    profile: ProfileJoined

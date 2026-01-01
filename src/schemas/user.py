from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.schemas.profile import ProfileOut, ProfileCreate, ProfileInternal


class UserBase(BaseModel):
    first_name: str
    last_name: str
    title: str


class UserOut(UserBase):
    id: UUID
    profile: ProfileOut

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    profile: ProfileCreate

    model_config = ConfigDict(from_attributes=True)


class UserInternal:
    id: UUID
    title: str
    profile: ProfileInternal

    model_config = ConfigDict(from_attributes=True)
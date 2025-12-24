from uuid import UUID

from pydantic import ConfigDict

from src.schemas.profile import ProfileOut


class UserBase:
    id: UUID
    first_name: str
    last_name: str
    title: str


class UserOut(UserBase):
    profile: ProfileOut

    model_config = ConfigDict(from_attributes=True)

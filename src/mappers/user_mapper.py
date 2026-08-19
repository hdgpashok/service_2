import uuid

from src.schemas.profile import ProfileJoined, ProfileExternal
from src.schemas.user import UserCreate, UserExternal, UserJoined
from src.models.user import UserModel
from src.models.profile import ProfileModel


def orm_to_dict(obj):
    if not obj:
        return {}
    return {
        column.name: getattr(obj, column.name)
        for column in obj.__table__.columns
    }



class UserMapper:
    @staticmethod
    def create_new_user(user: UserCreate, external_user: UserExternal):
        new_profile = ProfileModel(
            **user.profile.model_dump(exclude={'title', 'bio'}),
            id=external_user.profile.id
        )

        new_user = UserModel(id=external_user.id, profile=new_profile)

        for key, value in user.model_dump(exclude={'profile'}).items():
            setattr(new_user, key, value)

        return new_user

    @staticmethod
    def merge_user_data(internal, external):
        profile_data = {
            **(orm_to_dict(internal.profile) if internal.profile else {}),
            **external['profile']
        }

        return UserJoined(
            id=external['id'] or internal.id,
            first_name=internal.first_name,
            last_name=internal.last_name,
            title=external['title'],
            profile=ProfileJoined.model_validate(profile_data)
        )

    @staticmethod
    def create_external_schema(user: UserCreate):
        return UserExternal(
            id=uuid.uuid4(),
            title=user.title,
            profile=ProfileExternal(
                id=uuid.uuid4(),
                title=user.profile.title,
                bio=user.profile.bio
            )
        )
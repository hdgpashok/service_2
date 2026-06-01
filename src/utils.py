from src.schemas.profile import ProfileJoined
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


def create_new_user(user: UserCreate, external_user: UserExternal):
    new_profile = ProfileModel(
        **user.profile.model_dump(exclude={'title', 'bio'}),
        id=external_user.profile.id
    )

    new_user = UserModel(id=external_user.id, profile=new_profile)

    for key, value in user.model_dump(exclude={'profile'}).items():
        setattr(new_user, key, value)

    return new_user


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
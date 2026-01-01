import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.exceptions.not_found import ObjectNotFound

from src.models.user import UserModel

from src.models.profile import ProfileModel

from src.schemas.user import UserCreate, UserOut


class UserRepository:
    @staticmethod
    async def select(user_id: UUID, session: AsyncSession):
        query = (
            select(UserModel)
            .where(user_id == UserModel.id)
            .options(selectinload(UserModel.profile))
        )
        result = await session.execute(query)
        user = result.scalars().first()

        if not user:
            raise ObjectNotFound(object_id=user_id)

        return user

    @staticmethod
    async def create(user: UserCreate, session: AsyncSession) -> UserOut:
        new_profile = ProfileModel(**user.profile.model_dump())

        new_user = UserModel(id= uuid.uuid4(), profile=new_profile)
        user_data = user.model_dump(exclude={'profile'})

        for key, value in user_data.items():
            setattr(new_user, key, value)

        session.add(new_user)

        db_user = await UserRepository.select(new_user.id, session)
        return UserOut.model_validate(db_user)

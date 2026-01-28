from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.user import UserModel

from src.schemas.user import UserOut


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

        return user

    @staticmethod
    async def create(new_user: UserModel, session: AsyncSession) -> UserOut:

        session.add(new_user)

        db_user = await UserRepository.select(new_user.id, session)
        return UserOut.model_validate(db_user)

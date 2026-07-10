from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.profile import ProfileModel


class ProfileRepository:
    @staticmethod
    async def select(profile_id: UUID, session: AsyncSession):
        query = (
            select(ProfileModel)
            .where(profile_id == ProfileModel.id)
        )
        result = await session.execute(query)
        profile = result.scalars().first()

        return profile
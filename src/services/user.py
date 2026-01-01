from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.user import UserRepository
from src.schemas.user import UserCreate, UserOut


class UserService:
    @staticmethod
    async def create_user(user: UserCreate, session: AsyncSession) -> UserOut:
        return await UserRepository.create(user, session)
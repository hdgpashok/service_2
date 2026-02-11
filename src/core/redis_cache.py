from redis.asyncio import Redis

from src.core.config import Settings


settings = Settings()

rd = Redis(
    host=str(settings.REDIS_HOST),
    port=int(settings.REDIS_PORT),
    db=int(settings.REDIS_DB),
)

expire_time = 3600
from typing import Any, Optional

import ujson
from redis.asyncio import Redis
from redis.exceptions import RedisError


class CacheService:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def get(self, key: str):
        try:
            data = await self.redis.get(key)
            if data is None:
                return None

            if isinstance(data, bytes):
                data = data.decode("utf-8")

            return ujson.loads(data)

        except (RedisError, ujson.JSONDecodeError, UnicodeDecodeError):
            return None

    async def set(self, key: str, value: Any, expire: int = 3600):
        try:
            serialized = ujson.dumps(value)
            await self.redis.set(key, serialized, ex=expire)
            return True
        except (RedisError, TypeError):
            return False

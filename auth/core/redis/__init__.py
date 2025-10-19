from redis.asyncio import Redis

from core.config import settings


class RedisClient:
    redis_client: Redis = Redis(
        host=settings.redis.host,
        port=settings.redis.port,
        db=settings.redis.db,
        decode_responses=settings.redis.decode_responses,
    )

    @classmethod
    async def connect(cls):
        await cls.redis_client.ping()

    @classmethod
    async def close(cls):
        if cls.redis_client:
            await cls.redis_client.close()

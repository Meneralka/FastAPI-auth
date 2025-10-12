import json
import functools
import hashlib
from typing import Callable, Any, Awaitable

from redis.asyncio import Redis

redis = Redis(host="localhost", port=6379, decode_responses=True)


def redis_cache(
    ttl: int = 60,
    namespace: str = "default",
    read: bool = False,
    write: bool = False,
):
    """
    Кэширование с автоматической очисткой по namespace.
    - ttl: время жизни кэша (секунды)
    - namespace: логическая группа ключей (например 'users')
    - read: кэшировать результат (True)
    - write: очищать кэш при записи (True)
    """
    def decorator(func: Callable[..., Awaitable[Any]]):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if write:
                pattern = f"{namespace}:*"
                async for key in redis.scan_iter(match=pattern):
                    await redis.delete(key)

                return await func(*args, **kwargs)

            if read:
                raw_key = f"{namespace}:{func.__module__}:{func.__name__}:{args}:{kwargs}"
                key = hashlib.sha256(raw_key.encode()).hexdigest()
                cache_key = f"{namespace}:{key}"

                cached = await redis.get(cache_key)
                if cached:
                    return json.loads(cached)

                result = await func(*args, **kwargs)

                await redis.setex(cache_key, ttl, json.dumps(result, default=str))
                return result

            return await func(*args, **kwargs)

        return wrapper
    return decorator
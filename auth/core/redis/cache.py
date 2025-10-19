import functools
import hashlib
import json
from typing import (
    Type,
    Callable,
    Awaitable,
    Any,
    Sequence
)

from pydantic import BaseModel
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from core.redis import RedisClient


class Cache:
    redis_client: Redis = RedisClient.redis_client

    @classmethod
    def _make_key(cls, namespace: str, func: Callable[..., Awaitable[Any]], kwargs: dict) -> str:
        """Создаёт хэшированный ключ для Redis."""
        raw = f"{namespace}:{func.__module__}:{func.__name__}:{kwargs}"
        return f"{namespace}:{hashlib.sha256(raw.encode()).hexdigest()}"

    @classmethod
    async def _clear_namespace(cls, namespace: str):
        """Удаляет все ключи для указанного namespace."""
        pattern = f"{namespace}:*"
        async for key in cls.redis_client.scan_iter(match=pattern):
            await cls.redis_client.delete(key)

    @classmethod
    def redis(
        cls,
        ttl: int = 90,
        namespace: str = "default",
        read: bool = False,
        write: bool = False,
        model_class: Type[BaseModel] | Type[Sequence[BaseModel]] = None,
    ):
        def decorator(func: Callable[..., Awaitable[Any]]):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                # Очистка от AsyncSession
                cleaned_kwargs = {
                    k: (None if isinstance(v, AsyncSession) else v)
                    for k, v in kwargs.items()
                }

                # Если режим записи — очистить кэш и выполнить функцию
                if write:
                    await cls._clear_namespace(namespace)
                    return await func(*args, **kwargs)

                # Если режим чтения — попытка прочитать из кэша
                if read:
                    cache_key = cls._make_key(namespace, func, cleaned_kwargs)
                    cached = await cls.redis_client.get(cache_key)

                    if cached:
                        data = json.loads(cached)
                        if model_class:
                            if isinstance(data, list):
                                return [model_class.model_validate(i) for i in data]
                            return model_class.model_validate(data)
                        return data

                    # Если данных нет в кэше — выполняем и сохраняем
                    result = await func(*args, **kwargs)
                    if not result:
                        return result

                    if model_class:
                        if isinstance(result, list):
                            json_data = json.dumps(
                                [model_class.model_validate(i).model_dump() for i in result]
                            )
                        else:
                            json_data = model_class.model_validate(result).model_dump_json()
                    else:
                        json_data = json.dumps(result)

                    await cls.redis_client.setex(cache_key, ttl, json_data)
                    return result

                # Без кэширования
                return await func(*args, **kwargs)

            return wrapper

        return decorator

from typing import Any, cast, Awaitable

from redis.commands.search import AsyncPipeline


class RedisRepository:
    def __init__(self, pipe: AsyncPipeline):
        self.pipe = pipe


class RedisCacheRepository(RedisRepository):
    async def get(self, key: str) -> dict[str, Any] | None:
        pass

    async def set(
        self, key: str, value: dict[str, Any], ttl: int | None = None
    ) -> None:
        pass

    async def delete(self, key: str) -> None:
        pass

    async def exists(self, key: str) -> None:
        pass

    async def clear(self, pattern: str) -> int:
        return -1

    async def hgetall(self, pattern: str) -> dict[str, Any] | None:
        await cast(Awaitable[dict], self.pipe.hgetall(pattern))
        result_execute: list = await self.pipe.execute()
        result: dict = result_execute[0]
        return result
